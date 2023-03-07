from api.v1.dependencies import AuthProvider
from finances.database.dao import UserDAO, DAO
from finances.exceptions.user import UserNotFound, UserExists
from finances.models import dto
from finances.models.enums.user_type import UserType


async def signup(
        user: dict,
        auth_provider: AuthProvider,
        dao: DAO
):
    user_dto = await dao.user.create(
        dto.UserWithCreds(username=user['username'],
                          hashed_password=auth_provider.get_password_hash(
                              user['password']),
                          user_type=UserType.USER))
    base_currency = await dao.currency.get_by_code('USD')
    if base_currency:
        await dao.user.set_base_currency(user_dto, base_currency.id)
    await dao.commit()


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
