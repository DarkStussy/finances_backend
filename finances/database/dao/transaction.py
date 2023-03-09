from _decimal import Decimal
from datetime import date
from uuid import UUID

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from finances.database.dao import BaseDAO
from finances.database.models import Transaction, Asset, TransactionCategory, \
    Currency
from finances.exceptions.base import MergeModelError, AddModelError
from finances.exceptions.transaction import AddTransactionError, \
    TransactionNotFound, MergeTransactionError
from finances.models import dto


class TransactionDAO(BaseDAO[Transaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(Transaction, session)

    async def get_by_id(self, transaction_id: int) -> dto.Transaction:
        transaction = await self._get_by_id(
            transaction_id,
            [joinedload(Transaction.asset).joinedload(Asset.currency),
             joinedload(Transaction.category)])
        if transaction is None:
            raise TransactionNotFound
        return transaction.to_dto()

    async def get_all(
            self,
            user_dto: dto.User,
            start_date: date,
            end_date: date,
            transaction_type: str | None = None
    ) -> list[dto.Transactions]:
        stmt = select(Transaction.created).where(
            Transaction.user_id == user_dto.id).filter(
            Transaction.created >= start_date,
            Transaction.created <= end_date).order_by(
            Transaction.created.desc()).distinct()
        if transaction_type:
            stmt = stmt.where(Transaction.category.has(
                TransactionCategory.type == transaction_type))
        result = await self.session.execute(stmt)
        transactions = []
        for created in result.fetchall():
            stmt = select(Transaction) \
                .where(
                Transaction.user_id == user_dto.id,
                Transaction.created == created[0]
            ) \
                .order_by(Transaction.created.desc(), Transaction.id.desc()) \
                .options(
                joinedload(Transaction.asset).joinedload(Asset.currency),
                joinedload(Transaction.category))
            if transaction_type:
                stmt = stmt.where(Transaction.category.has(
                    TransactionCategory.type == transaction_type))

            result = await self.session.execute(stmt)
            transactions.append(
                dto.Transactions(
                    created=created[0].date(),
                    transactions=[transaction.to_dto() for transaction in
                                  result.scalars().all()]
                )
            )

        return transactions

    async def get_total_by_period(
            self,
            user_dto: dto.User,
            start_date: date,
            end_date: date,
            transaction_type: str
    ) -> dict[str, Decimal]:
        stmt = select(Currency.code, Currency.rate_to_base_currency,
                      func.sum(Transaction.amount).label('total')) \
            .join(Transaction.asset).join(Transaction.category) \
            .join(Asset.currency) \
            .group_by(Currency.id, Currency.code) \
            .filter(Transaction.created >= start_date,
                    Transaction.created <= end_date) \
            .where(Transaction.category.has(TransactionCategory.type ==
                                            transaction_type),
                   Transaction.user_id == user_dto.id)
        result = await self.session.execute(stmt)
        result = result.fetchall()
        return {currency[0]: (currency[1], currency[2]) for currency in result}

    async def get_total_categories_by_period(
            self,
            user_dto: dto.User,
            start_date: date,
            end_date: date,
            transaction_type: str
    ) -> list[dto.TotalByCategoryAndCurrency]:
        stmt = select(TransactionCategory.title,
                      TransactionCategory.type,
                      Currency.code,
                      Currency.rate_to_base_currency,
                      func.sum(Transaction.amount).label('total')) \
            .join(Transaction.asset).join(Transaction.category) \
            .join(Asset.currency) \
            .group_by(Currency.id,
                      TransactionCategory.title,
                      TransactionCategory.type,
                      Currency.code) \
            .filter(Transaction.created >= start_date,
                    Transaction.created <= end_date) \
            .where(Transaction.category.has(TransactionCategory.type ==
                                            transaction_type),
                   Transaction.user_id == user_dto.id)
        result = await self.session.execute(stmt)
        result = result.fetchall()
        return [dto.TotalByCategoryAndCurrency(
            category=category[0],
            type=category[1],
            currency_code=category[2],
            rate_to_base_currency=category[3],
            total=category[4]
        ) for category in result]

    async def create(self, transaction_dto: dto.Transaction) \
            -> dto.Transaction:
        try:
            transaction = await self._create(transaction_dto)
        except AddModelError as e:
            raise AddTransactionError from e
        else:
            return transaction.to_dto(with_asset=False, with_category=False)

    async def merge(self, transaction_dto: dto.Transaction) -> dto.Transaction:
        try:
            transaction = await self._merge(transaction_dto)
        except MergeModelError as e:
            raise MergeTransactionError from e
        else:
            return transaction.to_dto(with_asset=False, with_category=False)

    async def delete_by_id(
            self,
            transaction_id: int,
            user_id: UUID
    ) -> Transaction | None:
        stmt = delete(Transaction) \
            .where(Transaction.id == transaction_id,
                   Transaction.user_id == user_id) \
            .returning(Transaction)
        transaction = await self.session.execute(stmt)
        transaction = transaction.scalar()
        return transaction.to_dto(
            with_asset=False, with_category=False) if transaction else None
