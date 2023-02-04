from finances.database.dao.currency import CurrencyDAO
from finances.models import dto


async def add_new_currency(currency: dict, user: dto.User,
                           currency_dao: CurrencyDAO) -> dto.Currency:
    currency_dto = dto.Currency.from_dict(currency)
    currency_dto.user = user.id
    currency_dto.is_custom = True
    return await currency_dao.create(currency_dto)
