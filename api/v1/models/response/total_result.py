from dataclasses import dataclass
from datetime import datetime, date
from uuid import UUID

from .transaction import TransactionResponse


@dataclass
class TotalResult:
    total: float
    server_time: datetime = datetime.utcnow()


@dataclass
class TotalAssetResult:
    asset_id: UUID
    total: float
    server_time: datetime = datetime.utcnow()


@dataclass
class TransactionsResponse:
    created: date
    transactions: list[TransactionResponse]
