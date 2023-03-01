from backend.finances.database.dao import UserDAO
from backend.finances.exceptions.user import UserNotFound, UserExists
from backend.finances.models import dto


async def set_username(user: dto.User,
                       username: str,
                       user_dao: UserDAO):
    try:
        await user_dao.get_by_username(username)
    except UserNotFound:
        await user_dao.set_username(user, username)
        await user_dao.commit()
    else:
        raise UserExists


async def set_password(user: dto.User,
                       new_hashed_password: str,
                       user_dao: UserDAO):
    await user_dao.set_password(user, new_hashed_password)
    await user_dao.commit()
