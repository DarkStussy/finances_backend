import uuid

from sqlalchemy import String, Integer, ForeignKey, Numeric, Boolean, \
    BigInteger, func, DateTime, \
    PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, mapped_column

from finances.models import dto
from finances.models.enums.user_type import UserType


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'

    id = mapped_column(UUID(as_uuid=True),
                       primary_key=True,
                       default=uuid.uuid4)
    username = mapped_column(String,
                             unique=True,
                             nullable=False)
    password = mapped_column(String, nullable=False)
    user_type = mapped_column(String, nullable=False)

    def to_dto(self) -> dto.User:
        return dto.User(
            id=self.id,
            username=self.username,
            user_type=UserType(self.user_type)
        )


class UserConfiguration(Base):
    __tablename__ = 'user_config'

    id = mapped_column(UUID(as_uuid=True),
                       ForeignKey('user.id', ondelete='CASCADE'),
                       primary_key=True)
    base_currency = mapped_column(Integer,
                                  ForeignKey('currency.id',
                                             ondelete='CASCADE'))


class Balance(Base):
    __tablename__ = 'balance'

    id = mapped_column(UUID(as_uuid=True), primary_key=True,
                       default=uuid.uuid4)
    user = mapped_column(UUID(as_uuid=True),
                         ForeignKey('user.id', ondelete='CASCADE'),
                         nullable=False)
    title = mapped_column(String, nullable=False)
    currency = mapped_column(Integer,
                             ForeignKey('currency.id', ondelete='SET NULL'),
                             nullable=False)
    amount = mapped_column(Numeric, default=0)

    __table_args__ = (
        UniqueConstraint('user', 'title', name='u_balance1'),
    )


class Currency(Base):
    __tablename__ = 'currency'

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=False)
    short_name = mapped_column(String, nullable=False)
    is_custom = mapped_column(Boolean, default=True)
    rate_to_base_currency = mapped_column(Numeric)
    user = mapped_column(UUID(as_uuid=True),
                         ForeignKey('user.id', ondelete='CASCADE'))


class Transaction(Base):
    __tablename__ = 'transaction'

    id = mapped_column(BigInteger, primary_key=True)
    user = mapped_column(UUID(as_uuid=True),
                         ForeignKey('user.id', ondelete='CASCADE'),
                         nullable=False)
    balance = mapped_column(String, nullable=False)
    category = mapped_column(String, nullable=False)
    type = mapped_column(String, nullable=False)
    amount = mapped_column(Numeric, nullable=False)
    created = mapped_column(DateTime(timezone=True), default=func.now())
    updated = mapped_column(DateTime(timezone=True), default=func.now())


class TransactionCategory(Base):
    __tablename__ = 'transaction_category'

    title = mapped_column(String, nullable=False)
    type = mapped_column(String, nullable=False)
    user = mapped_column(UUID(as_uuid=True),
                         ForeignKey('user.id', ondelete='CASCADE'),
                         nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('title', 'type', 'user', name='tran_category_pk'),
    )


class CryptoPortfolio(Base):
    __tablename__ = 'crypto_portfolio'

    id = mapped_column(UUID(as_uuid=True), primary_key=True,
                       default=uuid.uuid4)
    user = mapped_column(UUID(as_uuid=True),
                         ForeignKey('user.id', ondelete='CASCADE'),
                         nullable=False)
    title = mapped_column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint('user', 'title', name='u_crypto_portfolio1'),
    )


class CryptoCurrency(Base):
    __tablename__ = 'crypto_currency'

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=False)
    short_name = mapped_column(String, nullable=False)
    amount = mapped_column(Numeric, nullable=False)
    portfolio = mapped_column(UUID(as_uuid=True),
                              ForeignKey('crypto_portfolio.id',
                                         ondelete='CASCADE'))


class CryptoPortfolioTransaction(Base):
    __tablename__ = 'crypto_portfolio_transaction'

    id = mapped_column(BigInteger, primary_key=True)
    portfolio = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('crypto_portfolio.id', ondelete='CASCADE'),
        nullable=False)
    crypto_currency = mapped_column(
        Integer,
        ForeignKey('crypto_currency.id', ondelete='CASCADE'),
        nullable=False)
    amount = mapped_column(Numeric, nullable=False)
    created = mapped_column(DateTime(timezone=True), default=func.now())
    updated = mapped_column(DateTime(timezone=True), default=func.now())
