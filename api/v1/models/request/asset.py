from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class AssetCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    currency_id: int
    amount: Decimal = Field(max_digits=16)


class AssetChange(AssetCreate):
    id: UUID
