import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finances.database.dao import BaseDAO
from finances.database.models import Currency
from finances.models import dto


class CurrencyDAO(BaseDAO[Currency]):
    def __init__(self, session: AsyncSession):
        super().__init__(Currency, session)

    async def get_by_id(self, id_: int) -> dto.Currency | None:
        currency = await self._get_by_id(id_)
        return currency.to_dto() if currency else None

    async def get_all_by_user_id(self, user_id: uuid.UUID | None = None) \
            -> list[dto.Currency]:
        currencies = await self.session.execute(
            select(Currency).where(Currency.user == user_id))
        return [currency.to_dto() for currency in currencies.scalars().all()]

    async def create(self, currency_dto: dto.Currency) -> dto.Currency:
        currency = Currency.from_dto(currency_dto)
        self.save(currency)
        await self.session.commit()
        return currency.to_dto()
