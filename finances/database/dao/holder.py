from sqlalchemy.ext.asyncio import AsyncSession

from finances.database.dao.currency import CurrencyDAO
from finances.database.dao.user import UserDAO


class DAO:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user = UserDAO(self.session)
        self.currency = CurrencyDAO(self.session)

    async def commit(self):
        await self.session.commit()
