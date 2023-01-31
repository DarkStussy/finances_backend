from sqlalchemy.ext.asyncio import async_sessionmaker

from finances.database.dao import DAO


def dao_provider() -> DAO:
    raise NotImplementedError


class DatabaseProvider:
    def __init__(self, session: async_sessionmaker):
        self.session = session

    async def dao(self):
        async with self.session() as s:
            yield DAO(session=s)
