from decimal import Decimal
from dataclasses import dataclass
from datetime import date

from .transaction import Transaction


@dataclass
class TotalByCategoryAndCurrency:
    category: str
    type: str
    currency_code: str
    rate_to_base_currency: Decimal | None
    total: Decimal


@dataclass
class TotalByCategory:
    category: str
    type: str
    total: Decimal


@dataclass
class Transactions:
    created: date
    total_income: Decimal
    total_expense: Decimal
    transactions: list[Transaction]


@dataclass
class TotalsByAsset:
    income: Decimal
    expense: Decimal
