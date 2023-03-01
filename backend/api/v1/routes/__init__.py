from fastapi import APIRouter

from backend.api.v1.routes.asset import get_asset_router
from backend.api.v1.routes.currency import get_currency_router
from backend.api.v1.routes.transaction_category import \
    get_transaction_category_router
from backend.api.v1.routes.user import get_user_router
from backend.api.v1.routes.transaction import get_transaction_router


def setup_routers(api_router: APIRouter):
    api_router.include_router(get_user_router(), prefix='/user', tags=['user'])
    api_router.include_router(get_currency_router(), prefix='/currency',
                              tags=['currency'])
    api_router.include_router(get_asset_router(), prefix='/asset',
                              tags=['asset'])

    transaction_router = get_transaction_router()
    transaction_router.include_router(get_transaction_category_router(),
                                      prefix='/category')
    api_router.include_router(transaction_router,
                              prefix='/transaction',
                              tags=['transaction'])
