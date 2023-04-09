from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finances.database.dao import BaseDAO
from finances.database.models import CryptoCurrency
from finances.exceptions.base import AddModelError, MergeModelError
from finances.exceptions.crypto_currency import CryptoCurrencyNotFound, \
    CryptoCurrencyException
from finances.models import dto


class CryptoCurrencyDAO(BaseDAO[CryptoCurrency]):
    def __init__(self, session: AsyncSession):
        super().__init__(CryptoCurrency, session)

    async def get_by_id(self, crypto_currency_id: int) -> dto.CryptoCurrency:
        crypto_currency = await self._get_by_id(crypto_currency_id)
        if crypto_currency is None:
            raise CryptoCurrencyNotFound
        return crypto_currency.to_dto()

    async def get_all(
            self,
            code: str | None = None,
            ids: list[int] | None = None
    ) -> list[dto.CryptoCurrency]:
        stmt = select(CryptoCurrency)
        if code:
            stmt = stmt.filter(CryptoCurrency.code.like(f'%{code}%'))
        elif ids:
            stmt = stmt.where(CryptoCurrency.id.in_(ids))

        result = await self.session.execute(stmt)
        return [crypto_currency.to_dto() for crypto_currency in
                result.scalars().all()]

    async def create(self, crypto_currency_dto: dto.CryptoCurrency) \
            -> dto.CryptoCurrency:
        try:
            crypto_currency = await self._create(crypto_currency_dto)
        except AddModelError as e:
            raise CryptoCurrencyException(
                'Unable to add crypto currency') from e
        else:
            return crypto_currency.to_dto()

    async def merge(self, crypto_currency_dto: dto.CryptoCurrency) \
            -> dto.CryptoCurrency:
        try:
            crypto_currency = await self._merge(crypto_currency_dto)
        except MergeModelError as e:
            raise CryptoCurrencyException(
                'Unable to change crypto currency') from e
        else:
            return crypto_currency.to_dto()
