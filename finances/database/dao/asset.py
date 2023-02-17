from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from finances.database.dao import BaseDAO
from finances.database.models import Asset
from finances.exceptions.asset import AssetExists, AssetNotFound
from finances.models import dto


class AssetDAO(BaseDAO[Asset]):
    def __init__(self, session: AsyncSession):
        super().__init__(Asset, session)

    async def get_by_id(self, asset_id: UUID) -> dto.Asset:
        asset = await self._get_by_id(asset_id, [joinedload(Asset.currency)])
        if asset is None:
            raise AssetNotFound
        if asset.currency_id:
            return asset.to_dto()

        return asset.to_dto(with_currency=False)

    async def get_all(self, user_dto: dto.User) -> list[dto.Asset]:
        result = await self.session.execute(
            select(Asset).where(Asset.user_id == user_dto.id).options(
                joinedload(Asset.currency))
        )
        return [asset.to_dto(with_currency=bool(asset.currency_id)) for asset
                in result.scalars().all()]

    async def create(self, asset_dto: dto.Asset) -> dto.Asset:
        try:
            asset = Asset.from_dto(asset_dto)
            self.save(asset)
            await self.commit()
        except IntegrityError as e:
            if e.code == 'gkpj':
                await self.session.rollback()
                raise AssetExists from e
        else:
            return asset.to_dto(with_currency=False)

    async def merge(self, asset_dto: dto.Asset) -> dto.Asset:
        try:
            asset = Asset.from_dto(asset_dto)
            asset.id = asset_dto.id
            await self.session.merge(asset)
            await self.commit()
        except IntegrityError as e:
            if e.code == 'gkpj':
                await self.session.rollback()
                raise AssetExists from e
        else:
            return asset.to_dto(with_currency=False)

    async def delete_by_id(self, asset_id: UUID, user_id: UUID) -> UUID:
        stmt = delete(Asset) \
            .where(Asset.id == asset_id,
                   Asset.user_id == user_id) \
            .returning(Asset.id)
        currency = await self.session.execute(stmt)
        await self.commit()
        return currency.scalar()
