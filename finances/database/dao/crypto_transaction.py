from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from finances.database.dao import BaseDAO
from finances.database.models import CryptoTransaction
from finances.exceptions.base import AddModelError, MergeModelError
from finances.exceptions.crypto_transaction import CryptoTransactionNotFound, \
    AddCryptoTransactionError, MergeCryptoTransactionError
from finances.models import dto


class CryptoTransactionDAO(BaseDAO[CryptoTransaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(CryptoTransaction, session)

    async def get_by_id(self, crypto_transaction_id: int) \
            -> dto.CryptoTransaction:
        crypto_transaction = await self._get_by_id(crypto_transaction_id)
        if crypto_transaction is None:
            raise CryptoTransactionNotFound
        return crypto_transaction.to_dto()

    async def get_all_by_crypto_asset(
            self,
            crypto_asset_id: int,
            portfolio_id: UUID,
            user_id: UUID
    ) -> list[dto.CryptoTransaction]:
        result = await self.session.execute(
            select(CryptoTransaction).where(
                CryptoTransaction.crypto_asset_id == crypto_asset_id,
                CryptoTransaction.portfolio_id == portfolio_id,
                CryptoTransaction.user_id == user_id
            )
        )
        return [crypto_transaction.to_dto() for crypto_transaction in
                result.scalars().all()]

    async def create(self, crypto_transaction_dto: dto.CryptoTransaction) \
            -> dto.CryptoTransaction:
        try:
            crypto_transaction = await self._create(crypto_transaction_dto)
        except AddModelError as e:
            raise AddCryptoTransactionError from e
        else:
            return crypto_transaction.to_dto()

    async def merge(self, crypto_transaction_dto: dto.CryptoTransaction) \
            -> dto.CryptoTransaction:
        try:
            crypto_transaction = await self._merge(crypto_transaction_dto)
        except MergeModelError as e:
            raise MergeCryptoTransactionError from e
        else:
            return crypto_transaction.to_dto()

    async def delete_by_id(self, crypto_transaction_id: int,
                           user_id: UUID) -> CryptoTransaction | None:
        stmt = delete(CryptoTransaction) \
            .where(CryptoTransaction.id == crypto_transaction_id,
                   CryptoTransaction.user_id == user_id) \
            .returning(CryptoTransaction)
        transaction = await self.session.execute(stmt)
        transaction = transaction.scalar()
        return transaction.to_dto() if transaction else None
