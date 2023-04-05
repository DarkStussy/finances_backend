from __future__ import annotations

from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime

from finances.models import dto

from .asset import AssetResponse
from .transaction_category import TransactionCategoryResponse


@dataclass
class TransactionResponse:
    id: int
    asset: AssetResponse
    category: TransactionCategoryResponse
    amount: Decimal
    created: datetime

    @classmethod
    def from_dto(cls, category_dto: dto.Transaction) \
            -> TransactionResponse:
        return TransactionResponse(
            id=category_dto.id,
            asset=AssetResponse.from_dto(category_dto.asset),
            category=TransactionCategoryResponse.from_dto(
                category_dto.category),
            amount=category_dto.amount,
            created=category_dto.created
        )
