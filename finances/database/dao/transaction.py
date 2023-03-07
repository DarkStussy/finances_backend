from datetime import date
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from finances.database.dao import BaseDAO
from finances.database.models import Transaction, Asset, TransactionCategory
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
    ) -> list[dto.Transaction]:
        stmt = select(Transaction).where(Transaction.user_id == user_dto.id) \
            .filter(Transaction.created >= start_date,
                    Transaction.created <= end_date) \
            .order_by(Transaction.created.desc(), Transaction.id.desc()) \
            .options(joinedload(Transaction.asset).joinedload(Asset.currency),
                     joinedload(Transaction.category))
        if transaction_type:
            stmt = stmt.where(Transaction.category.has(
                TransactionCategory.type == transaction_type))

        result = await self.session.execute(stmt)
        return [transaction.to_dto() for transaction in result.scalars().all()]

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
