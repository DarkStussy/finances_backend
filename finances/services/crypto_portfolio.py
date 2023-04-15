from uuid import UUID

from api.v1.dependencies import CurrencyAPI
from finances.database.dao import DAO, UserDAO
from finances.database.dao.crypto_portfolio import CryptoPortfolioDAO
from finances.exceptions.crypto_portfolio import CryptoPortfolioNotFound
from finances.models import dto
from finances.services.crypto_transaction import get_total_buy_by_crypto_asset


async def get_crypto_portfolio_by_id(
        crypto_portfolio_id: UUID,
        user: dto.User,
        crypto_portfolio_dao: CryptoPortfolioDAO
) -> dto.CryptoPortfolio:
    crypto_portfolio_dto = await crypto_portfolio_dao.get_by_id(
        crypto_portfolio_id)
    if crypto_portfolio_dto.user_id != user.id:
        raise CryptoPortfolioNotFound
    return crypto_portfolio_dto


async def add_crypto_portfolio(
        crypto_portfolio: dict,
        user: dto.User,
        dao: DAO
) -> dto.CryptoPortfolio:
    crypto_portfolio_dto = dto.CryptoPortfolio.from_dict(crypto_portfolio)
    crypto_portfolio_dto.user_id = user.id
    crypto_portfolio_dto = await dao.crypto_portfolio.create(
        crypto_portfolio_dto)
    base_crypto_portfolio = await dao.user.get_base_crypto_portfolio(user)
    if base_crypto_portfolio is None:
        await dao.user.set_base_crypto_portfolio(user, crypto_portfolio_dto.id)
    await dao.commit()
    return crypto_portfolio_dto


async def change_crypto_portfolio(
        crypto_portfolio: dict,
        user: dto.User,
        crypto_portfolio_dao: CryptoPortfolioDAO
) -> dto.CryptoPortfolio:
    changed_crypto_portfolio_dto = dto.CryptoPortfolio.from_dict(
        crypto_portfolio)
    crypto_portfolio_dto = await crypto_portfolio_dao.get_by_id(
        changed_crypto_portfolio_dto.id)
    if crypto_portfolio_dto.user_id != user.id:
        raise CryptoPortfolioNotFound

    changed_crypto_portfolio_dto.user_id = user.id
    changed_crypto_portfolio_dto = await crypto_portfolio_dao.merge(
        changed_crypto_portfolio_dto)
    await crypto_portfolio_dao.commit()

    return changed_crypto_portfolio_dto


async def delete_crypto_portfolio(
        crypto_portfolio_id: UUID,
        user: dto.User,
        crypto_portfolio_dao: CryptoPortfolioDAO
):
    deleted_crypto_portfolio_id = await crypto_portfolio_dao.delete_by_id(
        crypto_portfolio_id, user.id)
    if deleted_crypto_portfolio_id is None:
        raise CryptoPortfolioNotFound
    await crypto_portfolio_dao.commit()


async def get_base_crypto_portfolio(
        user: dto.User,
        user_dao: UserDAO
) -> dto.CryptoPortfolio:
    crypto_portfolio_dto = await user_dao.get_base_crypto_portfolio(
        user)
    if crypto_portfolio_dto is None:
        raise CryptoPortfolioNotFound
    return crypto_portfolio_dto


async def set_base_crypto_portfolio(
        crypto_portfolio_id: UUID,
        user: dto.User,
        dao: DAO
):
    crypto_portfolio_dto = await dao.crypto_portfolio.get_by_id(
        crypto_portfolio_id)
    if crypto_portfolio_dto.user_id != user.id:
        raise CryptoPortfolioNotFound

    await dao.user.set_base_crypto_portfolio(user, crypto_portfolio_id)
    await dao.commit()


async def get_total_by_portfolio(
        crypto_portfolio_id: UUID,
        user: dto.User,
        dao: DAO,
        currency_api: CurrencyAPI
) -> dto.TotalByPortfolio:
    crypto_assets = await dao.crypto_asset.get_all(crypto_portfolio_id,
                                                   user.id)
    crypto_codes = [crypto_asset.crypto_currency.code for crypto_asset in
                    crypto_assets]
    total = 0
    profit = 0
    if not crypto_codes:
        return dto.TotalByPortfolio(total=0, profit=profit)

    prices = await currency_api.get_crypto_currency_prices(crypto_codes)

    total_buy = 0
    for crypto_asset in crypto_assets:
        total += crypto_asset.amount * prices.get(
            crypto_asset.crypto_currency.code + 'USDT', 0)
        total_buy += await get_total_buy_by_crypto_asset(crypto_asset, dao)

    total = round(total, 2)
    profit = round(total - total_buy, 2)
    return dto.TotalByPortfolio(total=total, profit=profit)
