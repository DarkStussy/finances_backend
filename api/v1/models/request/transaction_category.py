from pydantic import BaseModel, Field

from finances.models.enums.transaction_type import TransactionType


class TransactionCategoryCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    type: TransactionType


class TransactionCategoryChange(BaseModel):
    id: int
    title: str = Field(min_length=3, max_length=100)
