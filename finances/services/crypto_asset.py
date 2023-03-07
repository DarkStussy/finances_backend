from finances.database.dao.crypto_asset import CryptoAssetDAO
from finances.exceptions.crypto_asset import CryptoAssetNotFound
from finances.models import dto


async def get_crypto_asset_by_id(
        crypto_asset_id: int,
        user: dto.User,
        crypto_asset_dao: CryptoAssetDAO
) -> dto.CryptoAsset:
    crypto_asset_dto = await crypto_asset_dao.get_by_id(crypto_asset_id)
    if crypto_asset_dto.user_id != user.id:
        raise CryptoAssetNotFound
    return crypto_asset_dto


async def delete_crypto_asset(
        crypto_asset_id: int,
        user: dto.User,
        crypto_asset_dao: CryptoAssetDAO
):
    deleted_crypto_asset_id = await crypto_asset_dao.delete_by_id(
        crypto_asset_id, user.id)
    if deleted_crypto_asset_id is None:
        raise CryptoAssetNotFound
    await crypto_asset_dao.commit()
