from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Body
from starlette import status

from api.v1.dependencies import get_current_user, dao_provider, AuthProvider, get_auth_provider
from api.v1.models.auth import UserCreate
from finances.database.dao.holder import DAO
from finances.exceptions.user import UserException
from finances.models import dto
from finances.services.user import set_password


async def get_me(current_user: dto.User = Depends(get_current_user)):
    return current_user


async def signup(user_create: UserCreate, auth_provider: AuthProvider = Depends(get_auth_provider),
                 dao: DAO = Depends(dao_provider)):
    try:
        await dao.user.create(user_create.username, auth_provider.get_password_hash(user_create.password))
    except UserException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    else:
        raise HTTPException(status_code=status.HTTP_200_OK)


async def set_password_route(
        password: str = Body(),
        auth: AuthProvider = Depends(get_auth_provider),
        user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider),
):
    hashed_password = auth.get_password_hash(password)
    await set_password(user, hashed_password, dao.user)
    raise HTTPException(status_code=200)


def user_router() -> APIRouter:
    router = APIRouter()
    router.add_api_route('/me', get_me, methods=['get'])
    router.add_api_route('/signup', signup, methods=['post'])
    router.add_api_route('/setpassword', set_password_route, methods=['post'])
    return router
