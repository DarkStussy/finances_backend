from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime, date
from uuid import UUID

from .transaction import TransactionResponse


@dataclass
class TotalResult:
    total: float
    server_time: datetime = datetime.utcnow()


@dataclass
class TotalByPortfolioResult:
    portfolio_id: UUID
    total: float
    profit: float
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
    total_income: float | None = None
    total_expense: float | None = None


@dataclass
class TotalByAssetResponse:
    asset_id: UUID
    total_income: Decimal
    total_expense: Decimal
    server_time: datetime = datetime.utcnow()
