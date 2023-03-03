from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from finances.models import dto


@dataclass
class CryptoPortfolioResponse:
    id: UUID
    title: str

    @classmethod
    def from_dto(cls, crypto_portfolio_dto: dto.CryptoPortfolio) \
            -> CryptoPortfolioResponse:
        return CryptoPortfolioResponse(
            id=crypto_portfolio_dto.id,
            title=crypto_portfolio_dto.title
        )
