from uuid import UUID

from pydantic import BaseModel, Field


class CryptoPortfolioCreate(BaseModel):
    title: str = Field(regex=r'^[\w\s]{3,50}$')


class CryptoPortfolioChange(CryptoPortfolioCreate):
    id: UUID
