from uuid import UUID

from finances.database.dao.asset import AssetDAO
from finances.database.dao.currency import CurrencyDAO
from finances.exceptions.asset import AssetNotFound
from finances.exceptions.currency import CurrencyNotFound
from finances.models import dto


async def get_asset_by_id(
        asset_id: UUID,
        user: dto.User,
        asset_dao: AssetDAO,
) -> dto.Asset:
    asset_dto = await asset_dao.get_by_id(asset_id)
    if asset_dto.user_id != user.id:
        raise AssetNotFound

    return asset_dto


async def create_asset(
        asset: dict,
        user: dto.User,
        asset_dao: AssetDAO,
        currency_dao: CurrencyDAO) -> dto.Asset:
    asset_dto = dto.Asset.from_dict(asset)
    asset_dto.user_id = user.id
    currency_dto = await currency_dao.get_by_id(asset_dto.currency_id)
    if currency_dto is None or (
            currency_dto.is_custom and currency_dto.user_id != user.id):
        raise CurrencyNotFound

    created_asset = await asset_dao.create(asset_dto)
    created_asset.currency = currency_dto
    return created_asset


async def change_asset(
        asset: dict,
        user: dto.User,
        asset_dao: AssetDAO,
        currency_dao: CurrencyDAO) -> dto.Asset:
    asset_dto = dto.Asset.from_dict(asset)
    asset_dto.user_id = user.id
    currency_dto = await currency_dao.get_by_id(asset_dto.currency_id)
    if currency_dto is None or (
            currency_dto.is_custom and currency_dto.user_id != user.id):
        raise CurrencyNotFound

    changed_asset = await asset_dao.merge(asset_dto)
    changed_asset.currency = currency_dto
    return changed_asset


async def delete_asset(
        asset_id: UUID,
        user: dto.User,
        asset_dao: AssetDAO,
):
    deleted_asset_id = await asset_dao.delete_by_id(asset_id, user.id)
    if deleted_asset_id is None:
        raise AssetNotFound
