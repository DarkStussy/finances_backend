from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from finances.database.dao import BaseDAO
from finances.database.models import Asset
from finances.exceptions.asset import AssetExists, AssetNotFound, \
    AssetCantBeDeleted
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
                                Asset.deleted.__eq__(False)).options(
                joinedload(Asset.currency))
        )
        return [asset.to_dto(with_currency=bool(asset.currency_id)) for asset
                in result.scalars().all()]

    async def create(self, asset_dto: dto.Asset) -> dto.Asset:
        asset = Asset.from_dto(asset_dto)
        self.save(asset)
        try:
            await self._flush(asset)
        except IntegrityError as e:
            raise AssetExists from e
        else:
            return asset.to_dto(with_currency=False)

    async def merge(self, asset_dto: dto.Asset) -> dto.Asset:
        asset = Asset.from_dto(asset_dto)
        asset = await self.session.merge(asset)
        try:
            await self._flush(asset)
        except IntegrityError as e:
            raise AssetExists from e
        else:
            return asset.to_dto(with_currency=False)

    async def delete_by_id(self, asset_id: UUID, user_id: UUID) -> UUID:
        stmt = delete(Asset) \
            .where(Asset.id == asset_id,
                   Asset.user_id == user_id) \
            .returning(Asset.id)
        asset = await self.session.execute(stmt)
        try:
            await self._flush(asset)
        except IntegrityError as e:
            raise AssetCantBeDeleted from e
        return asset.scalar()
