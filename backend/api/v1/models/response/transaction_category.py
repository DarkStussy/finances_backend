from __future__ import annotations

from dataclasses import dataclass

from backend.finances.models import dto
from backend.finances.models.enums.transaction_type import TransactionType


@dataclass
class TransactionCategoryResponse:
    id: int
    title: str
    type: TransactionType

    @classmethod
    def from_dto(cls, category_dto: dto.TransactionCategory) \
            -> TransactionCategoryResponse:
        return TransactionCategoryResponse(
            id=category_dto.id,
            title=category_dto.title,
            type=category_dto.type
        )
