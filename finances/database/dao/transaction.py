from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from finances.database.dao import BaseDAO
from finances.database.models import Transaction, Asset, TransactionCategory
from finances.exceptions.transaction import AddTransactionError, \
    TransactionNotFound, MergeTransactionError, TransactionCantBeDeleted
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
            transaction_type: str | None = None
    ) -> list[dto.Transaction]:
        stmt = select(Transaction).where(Transaction.user_id == user_dto.id) \
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
        transaction = Transaction(
            user_id=transaction_dto.user_id,
            asset_id=transaction_dto.asset_id,
            category_id=transaction_dto.category_id,
            amount=transaction_dto.amount,
            created=transaction_dto.created
        )
        self.save(transaction)
        try:
            await self._flush(transaction)
        except IntegrityError as e:
            raise AddTransactionError from e
        else:
            return transaction.to_dto(with_asset=False, with_category=False)

    async def merge(self, transaction_dto: dto.Transaction) -> dto.Transaction:
        transaction = Transaction.from_dto(transaction_dto)
        transaction = await self.session.merge(transaction)
        try:
            await self._flush(transaction)
        except IntegrityError as e:
            raise MergeTransactionError from e
        else:
            return transaction.to_dto(with_asset=False, with_category=False)

    async def delete_by_id(self, transaction_id: int, user_id: UUID) -> int:
        stmt = delete(Transaction) \
            .where(Transaction.id == transaction_id,
                   Transaction.user_id == user_id) \
            .returning(Transaction.id)
        transaction = await self.session.execute(stmt)
        try:
            await self._flush(transaction)
        except IntegrityError as e:
            raise TransactionCantBeDeleted from e
        return transaction.scalar()
