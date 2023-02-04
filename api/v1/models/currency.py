from _decimal import Decimal

from pydantic import BaseModel, Field


class CurrencyCreate(BaseModel):
    name: str = Field(regex='^[A-Za-z]{3,50}$')
    code: str = Field(regex='^[A-Z]{3}$')
    rate_to_base_currency: Decimal = Field(gt=0, max_digits=8,
                                           decimal_places=6)


class CreatedCurrency(BaseModel):
    id: int
    name: str
    code: str
    rate_to_base_currency: Decimal
