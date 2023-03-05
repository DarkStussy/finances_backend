import dataclasses
from dataclasses import dataclass


@dataclass
class CryptoCurrency:
    id: int | None
    name: str
    code: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
