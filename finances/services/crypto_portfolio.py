from uuid import UUID

from finances.database.dao.crypto_portfolio import CryptoPortfolioDAO
from finances.exceptions.crypto_portfolio import CryptoPortfolioNotFound
from finances.models import dto


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
        crypto_portfolio_dao: CryptoPortfolioDAO
) -> dto.CryptoPortfolio:
    crypto_portfolio_dto = dto.CryptoPortfolio.from_dict(crypto_portfolio)
    crypto_portfolio_dto.user_id = user.id
    crypto_portfolio_dto = await crypto_portfolio_dao.create(
        crypto_portfolio_dto)
    await crypto_portfolio_dao.commit()
    return crypto_portfolio_dto
