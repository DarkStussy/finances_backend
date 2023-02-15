from __future__ import annotations

from _decimal import Decimal

from pydantic import BaseModel, Field

from finances.models import dto


class CurrencyCreate(BaseModel):
    name: str = Field(regex=r'^[A-Za-z\s]{3,50}$')
    code: str = Field(regex='^[A-Z]{3}$')
    rate_to_base_currency: Decimal = Field(gt=0, max_digits=8,
                                           decimal_places=6)


class CurrencyChange(CurrencyCreate):
    id: int

    @classmethod
    def from_dto(cls, currency_dto: dto.Currency) -> CurrencyChange:
        return CurrencyChange(
            id=currency_dto.id,
            name=currency_dto.name,
            code=currency_dto.code,
            rate_to_base_currency=currency_dto.rate_to_base_currency,
        )


class CurrencyModel(CurrencyCreate):
    id: int
    is_custom: bool

    @classmethod
    def from_dto(cls, currency_dto: dto.Currency) -> CurrencyModel:
        return CurrencyModel(
            id=currency_dto.id,
            name=currency_dto.name,
            code=currency_dto.code,
            rate_to_base_currency=currency_dto.rate_to_base_currency,
            is_custom=currency_dto.is_custom
        )


class BaseCurrency(BaseModel):
    id: int
    name: str
    code: str
    is_custom: bool

    @classmethod
    def from_dto(cls, currency_dto: dto.Currency) -> BaseCurrency:
        return BaseCurrency(
            id=currency_dto.id,
            name=currency_dto.name,
            code=currency_dto.code,
            is_custom=currency_dto.is_custom
        )
