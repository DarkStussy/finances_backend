import uuid

from sqlalchemy import select, delete, or_
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

    async def get_by_code(self, code: str, user_id: uuid.UUID | None = None) \
            -> dto.Currency | None:
        result = await self.session.execute(
            select(Currency).where(Currency.code == code,
                                   Currency.user_id == user_id)
        )
        currency = result.scalar_one_or_none()
        return currency.to_dto() if currency else None

    async def get_all(self, code: str | None = None,
                      user_id: uuid.UUID | None = None,
                      all_currencies: bool = False) \
            -> list[dto.Currency]:
        stmt = select(Currency).where(Currency.user_id == user_id)
        if all_currencies:
            stmt = select(Currency).where(or_(Currency.user_id == user_id,
                                              Currency.user_id.is_(None)))
        if code:
            stmt = stmt.where(Currency.code.like(f'%{code}%'))
        currencies = await self.session.execute(stmt)
        return [currency.to_dto() for currency in currencies.scalars().all()]

    async def create(self, currency_dto: dto.Currency) -> dto.Currency:
        currency = await self._create(currency_dto)
        return currency.to_dto()

    async def merge(self, currency_dto: dto.Currency) -> dto.Currency:
        currency = await self._merge(currency_dto)
        return currency.to_dto()

    async def delete_by_id(self, currency_id: int, user_id: uuid.UUID) -> int:
        stmt = delete(Currency) \
            .where(Currency.id == currency_id,
                   Currency.user_id == user_id) \
            .returning(Currency.id)
        currency = await self.session.execute(stmt)
        return currency.scalar()
