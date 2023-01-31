from finances.database.dao import UserDAO
from finances.models import dto


async def set_password(user: dto.User, new_hashed_password: str, user_dao: UserDAO):
    await user_dao.set_password(user, new_hashed_password)
    await user_dao.commit()
