from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from finances.database.dao import BaseDAO
from finances.database.models import Asset
from finances.exceptions.asset import AssetExists, AssetNotFound
from finances.exceptions.base import AddModelError, MergeModelError
from finances.models import dto


class AssetDAO(BaseDAO[Asset]):
    def __init__(self, session: AsyncSession):
        super().__init__(Asset, session)

    async def get_by_id(self, asset_id: UUID) -> dto.Asset:
        asset = await self._get_by_id(asset_id, [joinedload(Asset.currency)])
        if asset is None or asset.deleted:
            raise AssetNotFound
        if asset.currency_id:
            return asset.to_dto()

        return asset.to_dto(with_currency=False)

    async def get_all(self, user_dto: dto.User) -> list[dto.Asset]:
        result = await self.session.execute(
            select(Asset).where(Asset.user_id == user_dto.id,
                                Asset.deleted.is_(False)).options(
                joinedload(Asset.currency)).order_by(Asset.title)
        )
        return [asset.to_dto(with_currency=bool(asset.currency_id)) for asset
                in result.scalars().all()]

    async def create(self, asset_dto: dto.Asset) -> dto.Asset:
        try:
            asset = await self._create(asset_dto)
        except AddModelError as e:
            raise AssetExists from e
        else:
            return asset.to_dto(with_currency=False)

    async def merge(self, asset_dto: dto.Asset) -> dto.Asset:
        try:
            asset = await self._merge(asset_dto)
        except MergeModelError as e:
            raise AssetExists from e
        else:
            return asset.to_dto(with_currency=False)

    async def delete_by_id(self, asset_id: UUID, user_id: UUID) -> UUID:
        stmt = delete(Asset) \
            .where(Asset.id == asset_id,
                   Asset.user_id == user_id) \
            .returning(Asset.id)
        asset = await self.session.execute(stmt)
        return asset.scalar()

    async def update_amount(
            self,
            amount: Decimal,
            asset_id: UUID,
            user_id: UUID
    ):
        stmt = update(Asset).where(
            Asset.id == asset_id,
            Asset.user_id == user_id
        ).values(amount=Asset.amount + amount)
        await self.session.execute(stmt)
