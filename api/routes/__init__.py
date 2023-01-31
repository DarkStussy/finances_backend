from fastapi import APIRouter

from api.routes.user import user_router


def setup_routers(main_api_router: APIRouter):
    main_api_router.include_router(user_router(), prefix='/user', tags=['user'])
