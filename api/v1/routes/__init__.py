from fastapi import APIRouter

from api.v1.routes.asset import asset_router
from api.v1.routes.currency import currency_router
from api.v1.routes.user import user_router


def setup_routers(api_router: APIRouter):
    api_router.include_router(user_router(), prefix='/users', tags=['user'])
    api_router.include_router(currency_router(), prefix='/currency',
                              tags=['currency'])
    api_router.include_router(asset_router(), prefix='/asset', tags=['asset'])
