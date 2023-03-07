from __future__ import annotations
from _decimal import Decimal
from dataclasses import dataclass
from uuid import UUID

from finances.models import dto


@dataclass
class CryptoAssetResponse:
    id: int
    portfolio_id: UUID
    crypto_currency: dto.CryptoCurrency
    amount: Decimal

    @classmethod
    def from_dto(cls, crypto_asset_dto: dto.CryptoAsset) \
            -> CryptoAssetResponse:
        return CryptoAssetResponse(
            id=crypto_asset_dto.id,
            portfolio_id=crypto_asset_dto.portfolio_id,
            crypto_currency=crypto_asset_dto.crypto_currency,
            amount=crypto_asset_dto.amount
        )
