from __future__ import annotations

import uuid
from _decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, Numeric, Boolean, \
    BigInteger, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship

from finances.models import dto
from finances.models.enums.transaction_type import TransactionType
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

    config: Mapped['UserConfiguration'] = relationship()

    def to_dto(self) -> dto.User:
        return dto.User(
            id=self.id,
            username=self.username,
            user_type=UserType(self.user_type)
        )

    @classmethod
    def from_dto(cls, user_dto: dto.UserWithCreds) -> User:
        return User(
            id=user_dto.id,
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
    base_currency_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('currency.id', ondelete='SET NULL'),
        nullable=True)

    base_crypto_portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('crypto_portfolio.id', ondelete='SET NULL'),
        nullable=True
    )

    base_currency: Mapped['Currency'] = relationship()
    base_crypto_portfolio: Mapped['CryptoPortfolio'] = relationship()


class Asset(Base):
    __tablename__ = 'asset'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                                          default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey('user.id',
                                                          ondelete='CASCADE'),
                                               nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    currency_id: Mapped[int] = mapped_column(Integer,
                                             ForeignKey('currency.id',
                                                        ondelete='SET NULL'),
                                             nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric, default=0)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped['User'] = relationship()
    currency: Mapped['Currency'] = relationship()

    __table_args__ = (
        UniqueConstraint('user_id', 'title', name='unique_asset'),
    )

    def to_dto(self, with_currency: bool = True) -> dto.Asset:
        return dto.Asset(
            id=self.id,
            user_id=self.user_id,
            title=self.title,
            currency_id=self.currency_id,
            amount=self.amount,
            deleted=self.deleted,
            currency=self.currency.to_dto() if with_currency else None,
        )

    @classmethod
    def from_dto(cls, asset_dto: dto.Asset) -> Asset:
        return Asset(
            id=asset_dto.id,
            user_id=asset_dto.user_id,
            title=asset_dto.title,
            currency_id=asset_dto.currency_id,
            amount=asset_dto.amount,
            deleted=asset_dto.deleted
        )


class Currency(Base):
    __tablename__ = 'currency'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=True)
    rate_to_base_currency: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey('user.id',
                                                          ondelete='CASCADE'),
                                               nullable=True)

    user: Mapped['User'] = relationship()

    def to_dto(self) -> dto.Currency:
        return dto.Currency(
            id=self.id,
            name=self.name,
            code=self.code,
            is_custom=self.is_custom,
            rate_to_base_currency=self.rate_to_base_currency,
            user_id=self.user_id,
        )

    @classmethod
    def from_dto(cls, currency_dto: dto.Currency) -> Currency:
        return Currency(
            id=currency_dto.id,
            name=currency_dto.name,
            code=currency_dto.code,
            is_custom=currency_dto.is_custom,
            rate_to_base_currency=currency_dto.rate_to_base_currency,
            user_id=currency_dto.user_id,
        )


class Transaction(Base):
    __tablename__ = 'transaction'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey('user.id',
                                                          ondelete='CASCADE'),
                                               nullable=False)
    asset_id: Mapped[uuid.UUID] = mapped_column(UUID,
                                                ForeignKey('asset.id',
                                                           ondelete='CASCADE'),
                                                nullable=False)
    category_id: Mapped[int] = mapped_column(Integer,
                                             ForeignKey(
                                                 'transaction_category.id',
                                                 ondelete='CASCADE'),
                                             nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime)

    asset: Mapped['Asset'] = relationship()
    category: Mapped['TransactionCategory'] = relationship()

    def to_dto(self, with_asset: bool = True,
               with_category: bool = True) -> dto.Transaction:
        return dto.Transaction(
            id=self.id,
            user_id=self.user_id,
            asset_id=self.asset_id,
            category_id=self.category_id,
            amount=self.amount,
            created=self.created,
            asset=self.asset.to_dto() if with_asset else None,
            category=self.category.to_dto() if with_category else None
        )

    @classmethod
    def from_dto(cls, transaction_dto: dto.Transaction) -> Transaction:
        return Transaction(
            id=transaction_dto.id,
            user_id=transaction_dto.user_id,
            asset_id=transaction_dto.asset_id,
            category_id=transaction_dto.category_id,
            amount=transaction_dto.amount,
            created=transaction_dto.created
        )


class TransactionCategory(Base):
    __tablename__ = 'transaction_category'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey('user.id',
                                                          ondelete='CASCADE'),
                                               nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint('title', 'type', 'user_id',
                         name='tran_category_unique'),
    )

    def to_dto(self) -> dto.TransactionCategory:
        return dto.TransactionCategory(
            id=self.id,
            title=self.title,
            type=TransactionType(self.type),
            user_id=self.user_id,
            deleted=self.deleted
        )

    @classmethod
    def from_dto(cls, transaction_category_dto: dto.TransactionCategory) \
            -> TransactionCategory:
        return TransactionCategory(
            id=transaction_category_dto.id,
            title=transaction_category_dto.title,
            type=transaction_category_dto.type.value,
            user_id=transaction_category_dto.user_id,
            deleted=transaction_category_dto.deleted
        )


class CryptoPortfolio(Base):
    __tablename__ = 'crypto_portfolio'

    id: Mapped[int] = mapped_column(UUID(as_uuid=True), primary_key=True,
                                    default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey('user.id',
                                                          ondelete='CASCADE'),
                                               nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'title', name='u_crypto_portfolio1'),
    )

    def to_dto(self) -> dto.CryptoPortfolio:
        return dto.CryptoPortfolio(
            id=self.id,
            title=self.title,
            user_id=self.user_id,
        )

    @classmethod
    def from_dto(cls, crypto_portfolio_dto: dto.CryptoPortfolio) \
            -> CryptoPortfolio:
        return CryptoPortfolio(
            id=crypto_portfolio_dto.id,
            title=crypto_portfolio_dto.title,
            user_id=crypto_portfolio_dto.user_id
        )


class CryptoCurrency(Base):
    __tablename__ = 'crypto_currency'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    portfolio_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                                    ForeignKey(
                                                        'crypto_portfolio.id',
                                                        ondelete='CASCADE'),
                                                    nullable=False)


class CryptoPortfolioTransaction(Base):
    __tablename__ = 'crypto_portfolio_transaction'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('crypto_portfolio.id', ondelete='CASCADE'),
        nullable=False)
    crypto_currency_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('crypto_currency.id', ondelete='CASCADE'),
        nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime)
