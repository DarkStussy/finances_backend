from __future__ import annotations

from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from .asset import Asset
from .transaction_category import TransactionCategory


@dataclass
class Transaction:
    id: int | None
    user_id: UUID | None
    asset_id: UUID | None
    category_id: int | None
    amount: Decimal | None
    created: datetime | None
    asset: Asset | None = None
    category: TransactionCategory | None = None

    @classmethod
    def from_dict(cls, dct: dict) -> Transaction:
        return Transaction(
            id=dct.get('id'),
            user_id=dct.get('user_id'),
            asset_id=dct.get('asset_id'),
            category_id=dct.get('category_id'),
            amount=dct.get('amount'),
            created=dct.get('created')
        )
