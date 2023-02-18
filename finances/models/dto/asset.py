from __future__ import annotations

from _decimal import Decimal
from dataclasses import dataclass
from uuid import UUID
from .currency import Currency


@dataclass
class Asset:
    id: UUID | None
    user_id: UUID | None
    title: str | None
    currency_id: int | None
    amount: Decimal | None
    currency: Currency | None = None

    @classmethod
    def from_dict(cls, dct: dict) -> Asset:
        return Asset(
            id=dct.get('id'),
            user_id=dct.get('user_id'),
            title=dct.get('title'),
            currency_id=dct.get('currency_id'),
            amount=dct.get('amount')
        )
