from __future__ import annotations

from _decimal import Decimal
from dataclasses import dataclass
from uuid import UUID


@dataclass
class Currency:
    id: int | None
    name: str | None
    code: str | None
    is_custom: bool | None
    rate_to_base_currency: Decimal | None
    user_id: UUID | None

    @classmethod
    def from_dict(cls, dct: dict) -> Currency:
        return Currency(
            id=dct.get('id'),
            name=dct.get('name'),
            code=dct.get('code'),
            is_custom=dct.get('is_custom'),
            rate_to_base_currency=dct.get('rate_to_base_currency'),
            user_id=dct.get('user'),
        )
