from fastapi import Depends, APIRouter, HTTPException, Query
from starlette import status

from api.v1.dependencies import get_current_user, dao_provider
from api.v1.models.currency import CurrencyCreate, CurrencyModel
from finances.database.dao import DAO
from finances.models import dto
from finances.services.currency import add_new_currency


async def add_new_currency_route(
        currency: CurrencyCreate,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)):
    created_currency = await add_new_currency(currency.dict(), current_user,
                                              dao.currency)
    return CurrencyModel.from_dto(created_currency)


async def get_currency_by_id_route(
        currency_id: int,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)):
    currency = await dao.currency.get_by_id(currency_id)
    if currency is None or \
            currency.is_custom and currency.user != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return CurrencyModel.from_dto(currency)


async def get_currencies_route(
        include_defaults: bool = Query(default=False),
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)) -> list[dto.Currency]:
    currencies = await dao.currency.get_all_by_user_id(current_user.id)
    if not include_defaults:
        return currencies

    default_currencies = await dao.currency.get_all_by_user_id()
    return default_currencies + currencies


def currency_router() -> APIRouter:
    router = APIRouter()
    router.add_api_route('/add', add_new_currency_route, methods=['POST'],
                         response_model=CurrencyModel)
    router.add_api_route('/all', get_currencies_route, methods=['GET'])
    router.add_api_route('/{currency_id}', get_currency_by_id_route,
                         methods=['GET'], response_model=CurrencyModel)
    return router
