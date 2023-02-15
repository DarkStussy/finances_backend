from fastapi import Depends, APIRouter, HTTPException, Query
from starlette import status

from api.v1.dependencies import get_current_user, dao_provider
from api.v1.models.currency import CurrencyCreate, CurrencyModel, \
    BaseCurrency, CurrencyChange
from finances.database.dao import DAO
from finances.exceptions.currency import CurrencyNotFound, CurrencyCantBeBase
from finances.models import dto
from finances.services.currency import add_new_currency, change_currency, \
    delete_currency, set_base_currency


async def get_currency_by_id_route(
        currency_id: int,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)):
    currency = await dao.currency.get_by_id(currency_id)
    if currency is None or \
            currency.is_custom and currency.user != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if currency.is_custom:
        return CurrencyModel.from_dto(currency)
    else:
        return BaseCurrency.from_dto(currency)


async def add_new_currency_route(
        currency: CurrencyCreate,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)):
    created_currency = await add_new_currency(currency.dict(), current_user,
                                              dao.currency)
    return CurrencyModel.from_dto(created_currency)


async def change_currency_route(
        currency: CurrencyChange,
        current_user: dto.User = Depends(
            get_current_user),
        dao: DAO = Depends(dao_provider)):
    try:
        currency = await change_currency(currency.dict(), current_user,
                                         dao.currency)
    except CurrencyNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)

    return CurrencyModel.from_dto(currency)


async def delete_currency_route(
        currency_id: int,
        current_user: dto.User = Depends(
            get_current_user),
        dao: DAO = Depends(dao_provider)):
    try:
        await delete_currency(currency_id, current_user,
                              dao.currency)
    except CurrencyNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    else:
        raise HTTPException(status_code=status.HTTP_200_OK)


async def get_currencies_route(
        include_defaults: bool = Query(default=False),
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)) -> list[dto.Currency]:
    currencies = await dao.currency.get_all_by_user_id(current_user.id)
    if not include_defaults:
        return currencies

    default_currencies = await dao.currency.get_all_by_user_id()
    return default_currencies + currencies


async def get_base_currency_route(
        user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider),
):
    currency = await dao.user.get_base_currency(user)
    if currency is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Base currency not set')
    return BaseCurrency.from_dto(currency)


async def set_base_currency_route(
        currency_id: int,
        user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider),
):
    try:
        await set_base_currency(currency_id, user, dao)
    except CurrencyNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    except CurrencyCantBeBase as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e.message)
    else:
        raise HTTPException(status_code=status.HTTP_200_OK)


def currency_router() -> APIRouter:
    router = APIRouter()
    router.add_api_route('/add', add_new_currency_route,
                         methods=['POST'], response_model=CurrencyModel)
    router.add_api_route('/change', change_currency_route,
                         methods=['PUT'],
                         response_model=CurrencyModel)
    router.add_api_route('/delete/{currency_id}', delete_currency_route,
                         methods=['DELETE'])
    router.add_api_route('/all', get_currencies_route,
                         methods=['GET'])
    router.add_api_route('/base_currency', get_base_currency_route,
                         methods=['GET'], response_model=BaseCurrency)
    router.add_api_route('/base_currency/{currency_id}',
                         set_base_currency_route,
                         methods=['PUT'])
    router.add_api_route('/{currency_id}', get_currency_by_id_route,
                         methods=['GET'],
                         response_model=CurrencyModel | BaseCurrency)
    return router
