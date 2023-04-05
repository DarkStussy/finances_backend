from __future__ import annotations
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from finances.models.enums.transaction_type import CryptoTransactionType


@dataclass
class CryptoTransaction:
    id: int | None
    user_id: UUID | None
    portfolio_id: UUID | None
    crypto_asset_id: int | None
    type: CryptoTransactionType | None
    amount: Decimal | None
    price: Decimal | None
    created: datetime | None

    @classmethod
    def from_dict(cls, dct: dict) -> CryptoTransaction:
        return CryptoTransaction(
            id=dct.get('id'),
            user_id=dct.get('user_id'),
            portfolio_id=dct.get('portfolio_id'),
            crypto_asset_id=dct.get('crypto_asset_id'),
            type=dct.get('type'),
            amount=dct.get('amount'),
            price=dct.get('price'),
            created=dct.get('created')
        )
