from __future__ import annotations
from _decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from finances.models import dto
from finances.models.enums.transaction_type import CryptoTransactionType


@dataclass
class CryptoTransactionResponse:
    id: int | None
    portfolio_id: UUID
    crypto_asset_id: int
    type: CryptoTransactionType
    amount: Decimal
    price: Decimal
    created: datetime

    @classmethod
    def from_dto(cls, crypto_transaction_dto: dto.CryptoTransaction) \
            -> CryptoTransactionResponse:
        return CryptoTransactionResponse(
            id=crypto_transaction_dto.id,
            portfolio_id=crypto_transaction_dto.portfolio_id,
            crypto_asset_id=crypto_transaction_dto.crypto_asset_id,
            type=crypto_transaction_dto.type,
            amount=crypto_transaction_dto.amount,
            price=crypto_transaction_dto.price,
            created=crypto_transaction_dto.created
        )
