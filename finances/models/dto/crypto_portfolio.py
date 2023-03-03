from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class CryptoPortfolio:
    id: UUID | None
    title: str | None
    user_id: UUID | None

    @classmethod
    def from_dict(cls, dct: dict) -> CryptoPortfolio:
        return CryptoPortfolio(
            id=dct.get('id'),
            title=dct.get('title'),
            user_id=dct.get('user_id')
        )
