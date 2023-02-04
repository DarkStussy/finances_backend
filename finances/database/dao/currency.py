from sqlalchemy.ext.asyncio import AsyncSession

from finances.database.dao import BaseDAO
from finances.database.models import Currency
from finances.models import dto


class CurrencyDAO(BaseDAO[Currency]):
    def __init__(self, session: AsyncSession):
        super().__init__(Currency, session)

    async def create(self, currency_dto: dto.Currency):
        currency = Currency.from_dto(currency_dto)
        self.save(currency)
        await self.session.commit()
        return currency
