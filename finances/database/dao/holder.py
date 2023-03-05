from sqlalchemy.ext.asyncio import AsyncSession

from finances.database.dao.asset import AssetDAO
from finances.database.dao.crypto_currency import CryptoCurrencyDAO
from finances.database.dao.crypto_portfolio import CryptoPortfolioDAO
from finances.database.dao.currency import CurrencyDAO
from finances.database.dao.transaction import TransactionDAO
from finances.database.dao.transaction_category import TransactionCategoryDAO
from finances.database.dao.user import UserDAO


class DAO:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user = UserDAO(self.session)
        self.currency = CurrencyDAO(self.session)
        self.asset = AssetDAO(self.session)
        self.transaction_category = TransactionCategoryDAO(self.session)
        self.transaction = TransactionDAO(self.session)
        self.crypto_portfolio = CryptoPortfolioDAO(self.session)
        self.crypto_currency = CryptoCurrencyDAO(self.session)

    async def commit(self):
        await self.session.commit()
