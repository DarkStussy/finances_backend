from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class CurrencyCreate(BaseModel):
    name: str = Field(regex=r'^[A-Za-z\s]{3,50}$')
    code: str = Field(regex='^[A-Z]{3,5}$')
    rate_to_base_currency: Decimal = Field(gt=0, max_digits=8,
                                           decimal_places=6)


class CurrencyChange(CurrencyCreate):
    id: int
