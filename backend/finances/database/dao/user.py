from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from backend.finances.database.dao.base import BaseDAO
from backend.finances.database.models import User, UserConfiguration
from backend.finances.exceptions.user import UserExists, UserNotFound
from backend.finances.models import dto


class UserDAO(BaseDAO[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> dto.User:
        user = await self._get_by_username(username)
        return user.to_dto()

    async def get_by_username_with_password(self,
                                            username: str) \
            -> dto.UserWithCreds:
        user = await self._get_by_username(username)
        return user.to_dto().add_password(user.password)

    async def _get_by_username(self, username: str) -> User:
        result = await self.session.execute(
            select(User).where(User.username == username))
        try:
            user = result.scalar_one()
        except NoResultFound as e:
            raise UserNotFound from e
        else:
            return user

    async def create(self, user_dto: dto.UserWithCreds) -> dto.User:
        user = User.from_dto(user_dto)
        config = UserConfiguration(id=user.id)
        user.config = config
        self.save(user)
        try:
            await self._flush(user)
        except IntegrityError as e:
            raise UserExists from e
        else:
            return user.to_dto()

    async def set_username(self, user: dto.User, username: str):
        db_user = await self._get_by_id(user.id)
        db_user.username = username

    async def set_password(self, user: dto.User, hashed_password: str):
        db_user = await self._get_by_id(user.id)
        db_user.password = hashed_password

    async def get_base_currency(self, user: dto.User) -> dto.Currency | None:
        config = await self.session.get(UserConfiguration, user.id,
                                        options=[joinedload(
                                            UserConfiguration.base_currency)])
        return config.base_currency.to_dto() if config.base_currency else None

    async def set_base_currency(self, user: dto.User, currency_id: int):
        config = await self.session.get(UserConfiguration, user.id)
        config.base_currency_id = currency_id
        await self.session.merge(config)

    async def delete_by_id(self, id_: UUID):
        await self.session.execute(delete(User).where(User.id == id_))
