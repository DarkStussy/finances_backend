from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from finances.database.dao import BaseDAO
from finances.database.models import CryptoAsset
from finances.exceptions.base import AddModelError, MergeModelError
from finances.exceptions.crypto_asset import CryptoAssetNotFound, \
    AddCryptoAssetError, MergeCryptoAssetError
from finances.models import dto


class CryptoAssetDAO(BaseDAO[CryptoAsset]):
    def __init__(self, session: AsyncSession):
        super().__init__(CryptoAsset, session)

    async def get_by_id(self, crypto_asset_id: int) -> dto.CryptoAsset:
        crypto_asset = await self._get_by_id(
            crypto_asset_id,
            [joinedload(CryptoAsset.crypto_currency)]
        )
        if crypto_asset is None:
            raise CryptoAssetNotFound
        return crypto_asset.to_dto()

    async def get_by_currency(self, crypto_currency_id: int, user_id: UUID) -> dto.CryptoAsset | None:
        stmt = select(CryptoAsset).where(
            CryptoAsset.crypto_currency_id == crypto_currency_id,
            CryptoAsset.user_id == user_id
        )
        result = await self.session.execute(stmt)
        crypto_asset = result.scalar()
        return crypto_asset.to_dto(with_currency=False) if crypto_asset else None

    async def get_all(self, portfolio_id: UUID, user_id: UUID) \
            -> list[dto.CryptoAsset]:
        stmt = select(CryptoAsset).where(
            CryptoAsset.portfolio_id == portfolio_id,
            CryptoAsset.user_id == user_id
        ).options(joinedload(CryptoAsset.crypto_currency))
        result = await self.session.execute(stmt)
        return [crypto_asset.to_dto() for crypto_asset in
                result.scalars().all()]

    async def create(self, crypto_asset_dto: dto.CryptoAsset) \
            -> dto.CryptoAsset:
        try:
            crypto_asset = await self._create(crypto_asset_dto)
        except AddModelError as e:
            raise AddCryptoAssetError from e
        else:
            return crypto_asset.to_dto(with_currency=False)

    async def merge(self, crypto_asset_dto: dto.CryptoAsset) \
            -> dto.CryptoAsset:
        try:
            crypto_asset = await self._merge(crypto_asset_dto)
        except MergeModelError as e:
            raise MergeCryptoAssetError from e
        else:
            return crypto_asset.to_dto(with_currency=False)

    async def delete_by_id(
            self,
            crypto_asset_id: int,
            user_id: UUID
    ) -> int | None:
        stmt = delete(CryptoAsset).where(
            CryptoAsset.id == crypto_asset_id,
            CryptoAsset.user_id == user_id
        ).returning(CryptoAsset.id)
        result = await self.session.execute(stmt)
        return result.scalar()
