from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finances.database.dao import BaseDAO
from finances.database.models import CurrencyPrice
from finances.models import dto


class CurrencyPriceDAO(BaseDAO[CurrencyPrice]):
    def __init__(self, session: AsyncSession):
        super().__init__(CurrencyPrice, session)

    async def get_by_id(self, base: str,
                        quote: str) -> dto.CurrencyPrice | None:
        currency_price = await self._get_by_id((base, quote))
        return currency_price.to_dto() if currency_price else None

    async def get_prices(self, base: str, quotes: list[str]) \
            -> dict[str, dto.CurrencyPrice]:
        stmt = select(CurrencyPrice).where(
            CurrencyPrice.quote.in_(quotes),
            CurrencyPrice.base == base
        )
        result = await self.session.execute(stmt)
        return {currency_price.quote: currency_price.to_dto() for
                currency_price in result.scalars().all()}

    async def merge(
            self,
            currency_price_dto: dto.CurrencyPrice
    ) -> dto.CurrencyPrice:
        currency_price = CurrencyPrice.from_dto(currency_price_dto)
        currency_price = await self.session.merge(currency_price)
        await self._flush(currency_price)
        return currency_price.to_dto()

    async def add_many(self, currency_prices: list[dto.CurrencyPrice]):
        for currency_price_dto in currency_prices:
            currency_price = CurrencyPrice.from_dto(currency_price_dto)
            await self.session.merge(currency_price)
