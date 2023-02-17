from fastapi import APIRouter, Depends, HTTPException, Body
from starlette import status

from api.v1.dependencies import get_current_user, dao_provider, AuthProvider, \
    get_auth_provider
from api.v1.models.request.user import UserCreate
from finances.database.dao.holder import DAO
from finances.exceptions.user import UserException, UserExists
from finances.models import dto
from finances.models.enums.user_type import UserType
from finances.services.user import set_password, set_username


async def get_user_route(
        current_user: dto.User = Depends(get_current_user)) -> dto.User:
    return current_user


async def signup_route(
        user_create: UserCreate,
        auth_provider: AuthProvider = Depends(get_auth_provider),
        dao: DAO = Depends(dao_provider)):
    try:
        await dao.user.create(
            dto.UserWithCreds(username=user_create.username,
                              hashed_password=auth_provider.get_password_hash(
                                  user_create.password),
                              user_type=UserType.USER))
    except UserException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e.message)
    else:
        raise HTTPException(status_code=status.HTTP_200_OK)


async def set_username_route(
        username: str = Body(embed=True, regex=r'\w{3,32}'),
        user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider),
):
    try:
        await set_username(user, username, dao.user)
    except UserExists as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e.message)
    raise HTTPException(status_code=status.HTTP_200_OK)


async def set_password_route(
        password: str = Body(
            embed=True,
            regex='^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])'
                  '.{8,32}$'),
        auth: AuthProvider = Depends(get_auth_provider),
        user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider),
):
    hashed_password = auth.get_password_hash(password)
    await set_password(user, hashed_password, dao.user)
    raise HTTPException(status_code=status.HTTP_200_OK)


def user_router() -> APIRouter:
    router = APIRouter()
    router.add_api_route('/me', get_user_route, methods=['GET'])
    router.add_api_route('/signup', signup_route, methods=['POST'])
    router.add_api_route('/setusername', set_username_route, methods=['PUT'])
    router.add_api_route('/setpassword', set_password_route, methods=['PUT'])
    return router
