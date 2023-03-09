import dataclasses
from _decimal import Decimal
from dataclasses import dataclass


@dataclass
class CryptoCurrency:
    id: int | None
    name: str
    code: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class CryptoCurrencyPrice:
    code: str
    price: Decimal
