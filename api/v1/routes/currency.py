from fastapi import Depends, APIRouter

from api.v1.dependencies import get_current_user, dao_provider
from api.v1.models.currency import CurrencyCreate, CreatedCurrency
from finances.database.dao import DAO
from finances.models import dto
from finances.services.currency import add_new_currency


async def add_new_currency_route(currency: CurrencyCreate,
                                 current_user: dto.User = Depends(
                                     get_current_user),
                                 dao: DAO = Depends(dao_provider)):
    created_currency = await add_new_currency(currency.dict(), current_user,
                                              dao.currency)
    return CreatedCurrency(
        id=created_currency.id,
        name=created_currency.name,
        code=created_currency.code,
        rate_to_base_currency=created_currency.rate_to_base_currency
    )


def currency_router() -> APIRouter:
    router = APIRouter()
    router.add_api_route('/add', add_new_currency_route, methods=['POST'])
    return router
