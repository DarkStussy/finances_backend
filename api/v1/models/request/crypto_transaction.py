from decimal import Decimal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, validator, root_validator

from finances.models.enums.transaction_type import CryptoTransactionType


class BaseCryptoTransaction(BaseModel):
    type: CryptoTransactionType
    amount: Decimal = Field(gt=0, max_digits=16, decimal_places=8)
    price: Decimal = Field(gt=0, max_digits=16, decimal_places=8)
    created: datetime = Field(example='2023-02-19T22:04:00')

    @validator('created', pre=True)
    def validate_created(cls, value: str) -> datetime:
        return datetime.fromisoformat(value)


class CryptoTransactionCreate(BaseCryptoTransaction):
    portfolio_id: UUID
    crypto_asset_id: int | None = None
    crypto_currency_id: int | None = None

    @root_validator
    def one_of(cls, values: dict):
        crypto_asset_id = values.get('crypto_asset_id')
        crypto_currency_id = values.get('crypto_currency_id')
        if crypto_asset_id and crypto_currency_id or (
                crypto_asset_id is None) and (crypto_currency_id is None):
            raise ValueError(
                'Either crypto_asset_id or crypto_currency_id is required')
        return values


class CryptoTransactionChange(BaseCryptoTransaction):
    id: int
