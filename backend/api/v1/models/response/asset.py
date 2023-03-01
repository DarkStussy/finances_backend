from __future__ import annotations

from _decimal import Decimal
from dataclasses import dataclass
from uuid import UUID

from backend.finances.models import dto
from .currency import CurrencyResponse


@dataclass
class AssetResponse:
    id: UUID
    title: str
    amount: Decimal
    currency: CurrencyResponse | None

    @classmethod
    def from_dto(cls, asset_dto: dto.Asset) -> AssetResponse:
        return AssetResponse(
            id=asset_dto.id,
            title=asset_dto.title,
            amount=asset_dto.amount,
            currency=CurrencyResponse.from_dto(
                asset_dto.currency) if asset_dto.currency else None
        )
