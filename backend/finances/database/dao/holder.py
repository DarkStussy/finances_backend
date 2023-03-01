from sqlalchemy.ext.asyncio import AsyncSession

from backend.finances.database.dao.asset import AssetDAO
from backend.finances.database.dao.currency import CurrencyDAO
from backend.finances.database.dao.transaction import TransactionDAO
from backend.finances.database.dao.transaction_category import \
    TransactionCategoryDAO
from backend.finances.database.dao.user import UserDAO


class DAO:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user = UserDAO(self.session)
        self.currency = CurrencyDAO(self.session)
        self.asset = AssetDAO(self.session)
        self.transaction_category = TransactionCategoryDAO(self.session)
        self.transaction = TransactionDAO(self.session)

    async def commit(self):
        await self.session.commit()
