from _decimal import Decimal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, validator


class TransactionCreate(BaseModel):
    asset_id: UUID
    category_id: int
    amount: Decimal = Field(gt=0, max_digits=16)
    created: datetime = Field(description='Format: %Y-%m-%d %H:%M',
                              example='2023-02-19 22:04')

    @validator('created', pre=True)
    def validate_created(cls, value: str) -> datetime:
        return datetime.strptime(
            value,
            '%Y-%m-%d %H:%M'
        )


class TransactionChange(TransactionCreate):
    id: int
