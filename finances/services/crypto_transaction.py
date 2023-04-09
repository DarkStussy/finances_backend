from finances.database.dao import DAO
from finances.database.dao.crypto_transaction import CryptoTransactionDAO
from finances.exceptions.crypto_asset import CryptoAssetNotFound
from finances.exceptions.crypto_portfolio import CryptoPortfolioNotFound
from finances.exceptions.crypto_transaction import CryptoTransactionNotFound
from finances.models import dto
from finances.models.enums.transaction_type import CryptoTransactionType


async def get_crypto_transaction_by_id(
        crypto_transaction_id: int,
        user: dto.User,
        crypto_transaction_dao: CryptoTransactionDAO
) -> dto.CryptoTransaction:
    crypto_transaction_dto = await crypto_transaction_dao.get_by_id(
        crypto_transaction_id)
    if crypto_transaction_dto.user_id != user.id:
        raise CryptoTransactionNotFound
    return crypto_transaction_dto


async def add_crypto_transaction(
        crypto_transaction: dict,
        user: dto.User,
        dao: DAO
) -> dto.CryptoTransaction:
    portfolio_dto = await dao.crypto_portfolio.get_by_id(
        crypto_transaction['portfolio_id'])
    if portfolio_dto.user_id != user.id:
        raise CryptoPortfolioNotFound

    crypto_asset_id = crypto_transaction.get('crypto_asset_id')
    crypto_currency_id = crypto_transaction.get('crypto_currency_id')
    if crypto_currency_id:
        crypto_asset_dto = await dao.crypto_asset.get_by_currency(crypto_currency_id, user.id)
        if crypto_asset_dto is None:
            crypto_asset_dto = dto.CryptoAsset(
                id=None,
                user_id=user.id,
                portfolio_id=crypto_transaction['portfolio_id'],
                crypto_currency_id=crypto_currency_id,
                amount=None
            )
            crypto_asset_dto = await dao.crypto_asset.create(crypto_asset_dto)

        crypto_asset_id = crypto_asset_dto.id
    else:
        crypto_asset_dto = await dao.crypto_asset.get_by_id(crypto_asset_id)
        if crypto_asset_dto.user_id != user.id:
            raise CryptoAssetNotFound

    crypto_transaction['crypto_asset_id'] = crypto_asset_id
    crypto_transaction['user_id'] = user.id
    crypto_transaction_dto = dto.CryptoTransaction.from_dict(
        crypto_transaction)

    amount = crypto_transaction['amount']
    if crypto_transaction['type'] == CryptoTransactionType.BUY:
        crypto_asset_dto.amount += amount
    else:
        crypto_asset_dto.amount -= amount
    await dao.crypto_asset.merge(crypto_asset_dto)
    crypto_transaction_dto = await dao.crypto_transaction.create(
        crypto_transaction_dto)
    await dao.commit()
    return crypto_transaction_dto


async def change_crypto_transaction(
        crypto_transaction: dict,
        user: dto.User,
        dao: DAO
):
    crypto_transaction_dto = await dao.crypto_transaction.get_by_id(
        crypto_transaction['id'])
    if crypto_transaction_dto.user_id != user.id:
        raise CryptoTransactionNotFound

    crypto_asset_dto = await dao.crypto_asset.get_by_id(
        crypto_transaction_dto.crypto_asset_id)
    if crypto_transaction_dto.type == CryptoTransactionType.BUY:
        crypto_asset_dto.amount -= crypto_transaction_dto.amount
    elif crypto_transaction_dto.type == CryptoTransactionType.SELL:
        crypto_asset_dto.amount += crypto_transaction_dto.amount

    changed_transaction_type = crypto_transaction['type']
    amount = crypto_transaction['amount']
    if changed_transaction_type == CryptoTransactionType.BUY:
        crypto_asset_dto.amount += amount
    elif changed_transaction_type == CryptoTransactionType.SELL:
        crypto_asset_dto.amount -= amount

    await dao.crypto_asset.merge(crypto_asset_dto)

    price = crypto_transaction['price']
    created = crypto_transaction['created']
    crypto_transaction_dto.type = changed_transaction_type
    crypto_transaction_dto.amount = amount
    crypto_transaction_dto.price = price
    crypto_transaction_dto.created = created
    crypto_transaction_dto = await dao.crypto_transaction.merge(
        crypto_transaction_dto)
    await dao.commit()
    return crypto_transaction_dto


async def delete_crypto_transaction(
        crypto_transaction_id: int,
        user: dto.User,
        dao: DAO
):
    crypto_transaction_dto = await dao.crypto_transaction.delete_by_id(
        crypto_transaction_id, user.id)
    if crypto_transaction_dto is None:
        raise CryptoTransactionNotFound

    crypto_asset_dto = await dao.crypto_asset.get_by_id(
        crypto_transaction_dto.crypto_asset_id)
    if crypto_transaction_dto.type == CryptoTransactionType.BUY:
        crypto_asset_dto.amount -= crypto_transaction_dto.amount
    elif crypto_transaction_dto.type == CryptoTransactionType.SELL:
        crypto_asset_dto.amount += crypto_transaction_dto.amount

    await dao.crypto_asset.merge(crypto_asset_dto)
    await dao.commit()
