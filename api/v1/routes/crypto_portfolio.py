from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from api.v1.dependencies import get_current_user, dao_provider, CurrencyAPI, \
    currency_api_provider
from api.v1.dependencies.currency_api import CantGetPrice
from api.v1.models.request.crypto_portfolio import CryptoPortfolioCreate, \
    CryptoPortfolioChange
from api.v1.models.response.crypto_portfolio import CryptoPortfolioResponse
from api.v1.models.response.total_result import TotalResult
from finances.database.dao import DAO
from finances.exceptions.crypto_portfolio import CryptoPortfolioExists, \
    CryptoPortfolioNotFound
from finances.models import dto
from finances.services.crypto_portfolio import add_crypto_portfolio, \
    get_crypto_portfolio_by_id, change_crypto_portfolio, \
    delete_crypto_portfolio, get_base_crypto_portfolio, \
    set_base_crypto_portfolio, get_total_by_portfolio


async def get_crypto_portfolio_by_id_route(
        crypto_portfolio_id: UUID,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> CryptoPortfolioResponse:
    try:
        crypto_portfolio_dto = await get_crypto_portfolio_by_id(
            crypto_portfolio_id,
            current_user,
            dao.crypto_portfolio
        )
    except CryptoPortfolioNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    else:
        return CryptoPortfolioResponse.from_dto(crypto_portfolio_dto)


async def get_all_crypto_portfolios_route(
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> list[CryptoPortfolioResponse]:
    return await dao.crypto_portfolio.get_all(current_user)


async def add_crypto_portfolio_route(
        crypto_portfolio: CryptoPortfolioCreate,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> CryptoPortfolioResponse:
    try:
        crypto_portfolio_dto = await add_crypto_portfolio(
            crypto_portfolio.dict(),
            current_user,
            dao
        )
    except CryptoPortfolioExists as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e.message)
    else:
        return CryptoPortfolioResponse.from_dto(crypto_portfolio_dto)


async def change_crypto_portfolio_route(
        crypto_portfolio: CryptoPortfolioChange,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> CryptoPortfolioResponse:
    try:
        crypto_portfolio_dto = await change_crypto_portfolio(
            crypto_portfolio.dict(),
            current_user,
            dao.crypto_portfolio
        )
    except CryptoPortfolioNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    except CryptoPortfolioExists as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e.message)
    else:
        return CryptoPortfolioResponse.from_dto(crypto_portfolio_dto)


async def delete_crypto_portfolio_route(
        crypto_portfolio_id: UUID,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
):
    try:
        await delete_crypto_portfolio(crypto_portfolio_id, current_user,
                                      dao.crypto_portfolio)
    except CryptoPortfolioNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)

    raise HTTPException(status_code=status.HTTP_200_OK)


async def get_base_crypto_portfolio_route(
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> CryptoPortfolioResponse:
    try:
        crypto_portfolio_dto = await get_base_crypto_portfolio(
            current_user,
            dao.user
        )
    except CryptoPortfolioNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Base crypto portfolio not set')
    else:
        return CryptoPortfolioResponse.from_dto(crypto_portfolio_dto)


async def set_base_crypto_portfolio_route(
        crypto_portfolio_id: UUID,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
):
    try:
        await set_base_crypto_portfolio(crypto_portfolio_id, current_user, dao)
    except CryptoPortfolioNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    raise HTTPException(status_code=status.HTTP_200_OK)


async def get_total_by_portfolio_route(
        portfolio_id: UUID = Query(),
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider),
        currency_api: CurrencyAPI = Depends(currency_api_provider)
) -> TotalResult:
    try:
        total = await get_total_by_portfolio(portfolio_id, current_user, dao,
                                             currency_api)
    except CantGetPrice:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='Unable to calculate total price')
    else:
        return TotalResult(total=total)


def get_crypto_portfolio_router() -> APIRouter:
    router = APIRouter()
    router.add_api_route('/add', add_crypto_portfolio_route, methods=['POST'])
    router.add_api_route('/change', change_crypto_portfolio_route,
                         methods=['PUT'])
    router.add_api_route('/all', get_all_crypto_portfolios_route,
                         methods=['GET'])
    router.add_api_route('/totalPrice', get_total_by_portfolio_route,
                         methods=['GET'])
    router.add_api_route('/baseCryptoportfolio',
                         get_base_crypto_portfolio_route,
                         methods=['GET'])
    router.add_api_route('/baseCryptoportfolio/{crypto_portfolio_id}',
                         set_base_crypto_portfolio_route,
                         methods=['PUT'])
    router.add_api_route('/{crypto_portfolio_id}',
                         delete_crypto_portfolio_route,
                         methods=['DELETE'])
    router.add_api_route('/{crypto_portfolio_id}',
                         get_crypto_portfolio_by_id_route,
                         methods=['GET'])
    return router
