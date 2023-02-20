import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from finances.database.dao import BaseDAO
from finances.database.models import Currency
from finances.exceptions.currency import CurrencyNotFound
from finances.models import dto


class CurrencyDAO(BaseDAO[Currency]):
    def __init__(self, session: AsyncSession):
        super().__init__(Currency, session)

    async def get_by_id(self, id_: int) -> dto.Currency:
        currency = await self._get_by_id(id_)
        if currency is None:
            raise CurrencyNotFound
        return currency.to_dto()

    async def get_all_by_user_id(self, user_id: uuid.UUID | None = None) \
            -> list[dto.Currency]:
        currencies = await self.session.execute(
            select(Currency).where(Currency.user_id == user_id))
        return [currency.to_dto() for currency in currencies.scalars().all()]

    async def create(self, currency_dto: dto.Currency) -> dto.Currency:
        currency = Currency.from_dto(currency_dto)
        self.save(currency)
        await self._flush(currency)
        return currency.to_dto()

    async def merge(self, currency_dto: dto.Currency) -> dto.Currency:
        currency = await self.session.merge(
            Currency.from_dto(currency_dto)
        )
        await self._flush(currency)
        return currency.to_dto()

    async def delete_by_id(self, currency_id: int, user_id: uuid.UUID) -> int:
        stmt = delete(Currency) \
            .where(Currency.id == currency_id,
                   Currency.user_id == user_id) \
            .returning(Currency.id)
        currency = await self.session.execute(stmt)
        await self.commit()
        return currency.scalar()
