from __future__ import annotations

from _decimal import Decimal
from dataclasses import dataclass

from finances.models import dto


@dataclass
class CurrencyResponse:
    id: int
    name: str
    code: str
    is_custom: bool
    rate_to_base_currency: Decimal | None

    @classmethod
    def from_dto(cls, currency_dto: dto.Currency) -> CurrencyResponse:
        return CurrencyResponse(
            id=currency_dto.id,
            name=currency_dto.name,
            code=currency_dto.code,
            is_custom=currency_dto.is_custom,
            rate_to_base_currency=currency_dto.rate_to_base_currency
        )
