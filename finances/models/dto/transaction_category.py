from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from finances.models.enums.transaction_type import TransactionType


@dataclass
class TransactionCategory:
    id: int | None
    title: str | None
    type: TransactionType | None
    user_id: UUID | None

    @classmethod
    def from_dict(cls, dct: dict) -> TransactionCategory:
        return TransactionCategory(
            id=dct.get('id'),
            title=dct.get('title'),
            type=TransactionType(dct.get('type')),
            user_id=dct.get('user_id')
        )
