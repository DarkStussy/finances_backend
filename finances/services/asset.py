from uuid import UUID

from finances.database.dao import DAO
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


async def add_new_asset(
        asset: dict,
        user: dto.User,
        asset_dao: AssetDAO,
        currency_dao: CurrencyDAO) -> dto.Asset:
    asset_dto = dto.Asset.from_dict(asset)
    asset_dto.user_id = user.id
    currency_dto = await currency_dao.get_by_id(asset_dto.currency_id)
    if currency_dto.is_custom and currency_dto.user_id != user.id:
        raise CurrencyNotFound

    created_asset = await asset_dao.create(asset_dto)
    await asset_dao.commit()
    created_asset.currency = currency_dto
    return created_asset


async def change_asset(
        asset: dict,
        user: dto.User,
        asset_dao: AssetDAO,
        currency_dao: CurrencyDAO) -> dto.Asset:
    changed_asset_dto = dto.Asset.from_dict(asset)
    currency_dto = await currency_dao.get_by_id(changed_asset_dto.currency_id)
    if currency_dto.is_custom and currency_dto.user_id != user.id:
        raise CurrencyNotFound

    asset_dto = await asset_dao.get_by_id(changed_asset_dto.id)
    if asset_dto.user_id != user.id:
        raise AssetNotFound

    changed_asset_dto.user_id = user.id
    changed_asset = await asset_dao.merge(changed_asset_dto)
    await asset_dao.commit()
    changed_asset.currency = currency_dto
    return changed_asset


async def delete_asset(
        asset_id: UUID,
        user: dto.User,
        asset_dao: AssetDAO,
):
    deleted_asset_dto = await asset_dao.get_by_id(asset_id)
    if deleted_asset_dto.user_id != user.id:
        raise AssetNotFound

    deleted_asset_dto.deleted = True
    await asset_dao.merge(deleted_asset_dto)
    await asset_dao.commit()


async def get_total_asset(
        asset_id: UUID,
        user: dto.User,
        dao: DAO):
    asset_dto = await dao.asset.get_by_id(asset_id)
    if asset_dto is None or asset_dto.user_id != user.id:
        raise AssetNotFound

    base_currency = await dao.user.get_base_currency(user)
    if asset_dto.currency.is_custom:
        return round(
            asset_dto.amount / asset_dto.currency.rate_to_base_currency, 2)
    currency_price = await dao.currency_price.get_by_id(
        getattr(base_currency, 'code', 'USD'),
        asset_dto.currency.code)
    return round(asset_dto.amount / currency_price.price, 2)


async def get_total_assets(
        user: dto.User,
        dao: DAO
) -> float:
    assets = await dao.asset.get_all(user)
    if not assets:
        return 0

    currencies_codes = [
        asset.currency.code for asset in assets if
        asset.currency and not asset.currency.is_custom
    ]
    base_currency = await dao.user.get_base_currency(user)
    prices = await dao.currency_price.get_prices(
        getattr(base_currency, 'code', 'USD'), currencies_codes)
    amount = 0
    for asset in assets:
        if asset.currency:
            if asset.currency.is_custom:
                amount += asset.amount / asset.currency.rate_to_base_currency
            else:
                currency_price = prices.get(asset.currency.code)
                if currency_price is None:
                    rate = 1
                else:
                    rate = currency_price.price

                amount += asset.amount / rate

    return round(amount, 2)
