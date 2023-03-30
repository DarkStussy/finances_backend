from _decimal import Decimal
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
    total_income: float
    total_expense: float
    transactions: list[TransactionResponse]


@dataclass
class TotalByAssetResponse:
    asset_id: UUID
    total_income: Decimal
    total_expense: Decimal
    server_time: datetime = datetime.utcnow()
