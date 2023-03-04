from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from api.v1.dependencies import get_current_user, dao_provider
from api.v1.models.request.crypto_portfolio import CryptoPortfolioCreate, \
    CryptoPortfolioChange
from api.v1.models.response.crypto_portfolio import CryptoPortfolioResponse
from finances.database.dao import DAO
from finances.exceptions.crypto_portfolio import CryptoPortfolioExists, \
    CryptoPortfolioNotFound
from finances.models import dto
from finances.services.crypto_portfolio import add_crypto_portfolio, \
    get_crypto_portfolio_by_id, change_crypto_portfolio, \
    delete_crypto_portfolio


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
            dao.crypto_portfolio
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


def get_crypto_portfolio_router() -> APIRouter:
    router = APIRouter()
    router.add_api_route('/add', add_crypto_portfolio_route, methods=['POST'])
    router.add_api_route('/change', change_crypto_portfolio_route,
                         methods=['PUT'])
    router.add_api_route('/all', get_all_crypto_portfolios_route,
                         methods=['GET'])
    router.add_api_route('/{crypto_portfolio_id}',
                         delete_crypto_portfolio_route,
                         methods=['DELETE'])
    router.add_api_route('/{crypto_portfolio_id}',
                         get_crypto_portfolio_by_id_route,
                         methods=['GET'])
    return router
