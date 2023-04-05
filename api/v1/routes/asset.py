from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from api.v1.dependencies import get_current_user, dao_provider
from api.v1.models.request.asset import AssetCreate, AssetChange
from api.v1.models.response.asset import AssetResponse
from api.v1.models.response.total_result import TotalResult, TotalAssetResult
from finances.database.dao import DAO
from finances.exceptions.asset import AssetNotFound, AssetExists
from finances.exceptions.currency import CurrencyNotFound
from finances.models import dto
from finances.services.asset import add_new_asset, get_asset_by_id, \
    change_asset, delete_asset, get_total_assets, get_total_asset


async def get_asset_by_id_route(
        asset_id: UUID,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> AssetResponse:
    try:
        asset_dto = await get_asset_by_id(asset_id, current_user, dao.asset)
    except AssetNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    else:
        return AssetResponse.from_dto(asset_dto)


async def get_all_assets_route(
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> list[AssetResponse]:
    return await dao.asset.get_all(current_user)


async def add_new_asset_route(
        asset: AssetCreate,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> AssetResponse:
    try:
        asset_dto = await add_new_asset(asset.dict(), current_user, dao.asset,
                                        dao.currency)
    except CurrencyNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    except AssetExists as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e.message)

    return AssetResponse.from_dto(asset_dto)


async def change_asset_route(
        asset: AssetChange,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> AssetResponse:
    try:
        asset_dto = await change_asset(asset.dict(), current_user, dao.asset,
                                       dao.currency)
    except (CurrencyNotFound, AssetNotFound) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    return AssetResponse.from_dto(asset_dto)


async def delete_asset_route(
        asset_id: UUID,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
):
    try:
        await delete_asset(asset_id, current_user, dao.asset)
    except AssetNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    raise HTTPException(status_code=status.HTTP_200_OK)


async def get_total_asset_route(
        asset_id: UUID = Query(),
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> TotalAssetResult:
    try:
        total = await get_total_asset(asset_id, current_user, dao)
    except AssetNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    else:
        return TotalAssetResult(asset_id=asset_id, total=total)


async def get_total_assets_route(
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> TotalResult:
    total = await get_total_assets(current_user, dao)
    return TotalResult(total=total)


def get_asset_router() -> APIRouter:
    router = APIRouter()
    router.add_api_route('/add', add_new_asset_route, methods=['POST'])
    router.add_api_route('/change', change_asset_route, methods=['PUT'])
    router.add_api_route('/all', get_all_assets_route, methods=['GET'])
    router.add_api_route('/totalPrices', get_total_assets_route,
                         methods=['GET'])
    router.add_api_route('/total', get_total_asset_route, methods=['GET'])
    router.add_api_route('/{asset_id}', delete_asset_route,
                         methods=['DELETE'])
    router.add_api_route('/{asset_id}', get_asset_by_id_route, methods=['GET'])
    return router
