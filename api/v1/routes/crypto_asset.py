from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from api.v1.dependencies import get_current_user, dao_provider
from api.v1.models.response.crypto_asset import CryptoAssetResponse
from finances.database.dao import DAO
from finances.exceptions.crypto_asset import CryptoAssetNotFound
from finances.models import dto
from finances.services.crypto_asset import get_crypto_asset_by_id, \
    delete_crypto_asset, get_total_buy


async def get_crypto_asset_by_id_route(
        crypto_asset_id: int,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> CryptoAssetResponse:
    try:
        crypto_asset_dto = await get_crypto_asset_by_id(
            crypto_asset_id,
            current_user,
            dao.crypto_asset
        )
    except CryptoAssetNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    else:
        return CryptoAssetResponse.from_dto(crypto_asset_dto)


async def get_all_crypto_assets_route(
        portfolio_id: UUID,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> list[CryptoAssetResponse]:
    return await dao.crypto_asset.get_all(portfolio_id, current_user.id,
                                          without_transactions=True)


async def delete_crypto_asset_route(
        crypto_asset_id: int,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
):
    try:
        await delete_crypto_asset(crypto_asset_id, current_user,
                                  dao.crypto_asset)
    except CryptoAssetNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    raise HTTPException(status_code=status.HTTP_200_OK)


async def get_total_buy_route(
        crypto_asset_id: int,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> dto.TotalBuyCryptoAsset:
    try:
        total_buy = await get_total_buy(crypto_asset_id, current_user, dao)
    except CryptoAssetNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    else:
        return total_buy


def get_crypto_asset_router() -> APIRouter:
    router = APIRouter()
    router.add_api_route('/all', get_all_crypto_assets_route, methods=['GET'])
    router.add_api_route('/totalBuy', get_total_buy_route, methods=['GET'])
    router.add_api_route('/{crypto_asset_id}', delete_crypto_asset_route,
                         methods=['DELETE'])
    router.add_api_route('/{crypto_asset_id}', get_crypto_asset_by_id_route,
                         methods=['GET'])
    return router
