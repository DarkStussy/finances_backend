from __future__ import annotations
from decimal import Decimal
from dataclasses import dataclass
from uuid import UUID

from .crypto_currency import CryptoCurrency


@dataclass
class CryptoAsset:
    id: int | None
    user_id: UUID | None
    portfolio_id: UUID | None
    crypto_currency_id: int | None
    amount: Decimal | None

    crypto_currency: CryptoCurrency | None = None

    @classmethod
    def from_dict(cls, dct: dict) -> CryptoAsset:
        return CryptoAsset(
            id=dct.get('id'),
            user_id=dct.get('user_id'),
            portfolio_id=dct.get('portfolio_id'),
            crypto_currency_id=dct.get('crypto_currency_id'),
            amount=dct.get('amount')
        )
