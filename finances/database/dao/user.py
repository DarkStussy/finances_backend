from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from finances.database.dao.base import BaseDAO
from finances.database.models import User
from finances.exceptions.user import UserExists, UserNotFound
from finances.models import dto


class UserDAO(BaseDAO[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> dto.User:
        user = await self._get_by_username(username)
        return user.to_dto()

    async def get_by_username_with_password(self, username: str) -> dto.UserWithCreds:
        user = await self._get_by_username(username)
        return user.to_dto().add_password(user.password)

    async def _get_by_username(self, username: str) -> User:
        result = await self.session.execute(select(User).where(User.username == username))
        try:
            user = result.scalar_one()
        except NoResultFound as e:
            raise UserNotFound() from e
        else:
            return user

    async def create(self, username: str, password: str, is_admin: bool = False) -> dto.User:
        try:
            user = User(username=username, password=password, is_admin=is_admin)
            self.save(user)
            await self.session.commit()
        except IntegrityError as e:
            if e.code == 'gkpj':
                raise UserExists()
        else:
            return user.to_dto()

    async def set_password(self, user: dto.User, hashed_password: str):
        db_user = await self.get_by_id(user.id)
        db_user.hashed_password = hashed_password
        user.hashed_password = hashed_password
