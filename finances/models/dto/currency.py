from __future__ import annotations

from _decimal import Decimal
from dataclasses import dataclass
from uuid import UUID


@dataclass
class Currency:
    id: int | None = None
    name: str | None = None
    code: str | None = None
    is_custom: bool | None = None
    rate_to_base_currency: Decimal | None = None
    user: UUID | None = None

    @classmethod
    def from_dict(cls, dct: dict) -> Currency:
        rate = dct.get('rate_to_base_currency')
        return Currency(
            id=dct.get('id'),
            name=dct.get('name'),
            code=dct.get('code'),
            is_custom=dct.get('is_custom'),
            rate_to_base_currency=Decimal(rate) if rate else None,
            user=dct.get('user'),
        )
