from __future__ import annotations

import uuid
from _decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, Numeric, Boolean, \
    BigInteger, func, DateTime, \
    PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from finances.models import dto
from finances.models.enums.user_type import UserType


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                          primary_key=True,
                                          default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String,
                                          unique=True,
                                          nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    user_type: Mapped[str] = mapped_column(String, nullable=False)

    def to_dto(self) -> dto.User:
        return dto.User(
            id=self.id,
            username=self.username,
            user_type=UserType(self.user_type)
        )

    @classmethod
    def from_dto(cls, user_dto: dto.UserWithCreds) -> User:
        return User(
            username=user_dto.username,
            password=user_dto.hashed_password,
            user_type=user_dto.user_type.value,
        )


class UserConfiguration(Base):
    __tablename__ = 'user_config'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                          ForeignKey('user.id',
                                                     ondelete='CASCADE'),
                                          primary_key=True)
    base_currency: Mapped[int] = mapped_column(Integer,
                                               ForeignKey('currency.id',
                                                          ondelete='CASCADE'))


class Asset(Base):
    __tablename__ = 'asset'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                                          default=uuid.uuid4)
    user: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                            ForeignKey('user.id',
                                                       ondelete='CASCADE'),
                                            nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    currency: Mapped[int] = mapped_column(Integer,
                                          ForeignKey('currency.id',
                                                     ondelete='SET NULL'),
                                          nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric, default=0)

    __table_args__ = (
        UniqueConstraint('user', 'title', name='unique_asset'),
    )


class Currency(Base):
    __tablename__ = 'currency'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=True)
    rate_to_base_currency: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    user: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                            ForeignKey('user.id',
                                                       ondelete='CASCADE'))

    def to_dto(self) -> dto.Currency:
        return dto.Currency(
            id=self.id,
            name=self.name,
            code=self.code,
            is_custom=self.is_custom,
            rate_to_base_currency=self.rate_to_base_currency,
            user=self.user,
        )

    @classmethod
    def from_dto(cls, currency_dto: dto.Currency) -> Currency:
        return Currency(
            id=currency_dto.id,
            name=currency_dto.name,
            code=currency_dto.code,
            is_custom=currency_dto.is_custom,
            rate_to_base_currency=currency_dto.rate_to_base_currency,
            user=currency_dto.user,
        )


class Transaction(Base):
    __tablename__ = 'transaction'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                            ForeignKey('user.id',
                                                       ondelete='CASCADE'),
                                            nullable=False)
    asset: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                              default=func.now())
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                              default=func.now())


class TransactionCategory(Base):
    __tablename__ = 'transaction_category'

    title: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    user: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                            ForeignKey('user.id',
                                                       ondelete='CASCADE'),
                                            nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('title', 'type', 'user', name='tran_category_pk'),
    )


class CryptoPortfolio(Base):
    __tablename__ = 'crypto_portfolio'

    id: Mapped[int] = mapped_column(UUID(as_uuid=True), primary_key=True,
                                    default=uuid.uuid4)
    user: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                            ForeignKey('user.id',
                                                       ondelete='CASCADE'),
                                            nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint('user', 'title', name='u_crypto_portfolio1'),
    )


class CryptoCurrency(Base):
    __tablename__ = 'crypto_currency'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    portfolio: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                                 ForeignKey(
                                                     'crypto_portfolio.id',
                                                     ondelete='CASCADE'),
                                                 nullable=False)


class CryptoPortfolioTransaction(Base):
    __tablename__ = 'crypto_portfolio_transaction'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    portfolio: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('crypto_portfolio.id', ondelete='CASCADE'),
        nullable=False)
    crypto_currency: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('crypto_currency.id', ondelete='CASCADE'),
        nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                              default=func.now())
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                              default=func.now())
