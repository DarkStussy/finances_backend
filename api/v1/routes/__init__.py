from fastapi import APIRouter

from api.v1.routes.user import user_router


def setup_routers(api_router: APIRouter):
    api_router.include_router(user_router(), prefix='/users', tags=['user'])
