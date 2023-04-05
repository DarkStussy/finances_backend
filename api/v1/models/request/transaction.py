from decimal import Decimal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, validator


class TransactionCreate(BaseModel):
    asset_id: UUID
    category_id: int
    amount: Decimal = Field(gt=0, max_digits=16, decimal_places=8)
    created: datetime = Field(example='2023-02-19T22:04:00')

    @validator('created', pre=True)
    def validate_created(cls, value: str) -> datetime:
        return datetime.fromisoformat(value)


class TransactionChange(TransactionCreate):
    id: int
