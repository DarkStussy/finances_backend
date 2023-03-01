from finances.database.dao import DAO
from finances.database.dao.currency import CurrencyDAO
from finances.exceptions.currency import CurrencyNotFound, CurrencyCantBeBase
from finances.models import dto


async def get_currency_by_id(
        currency_id: int,
        user: dto.User,
        currency_dao: CurrencyDAO
) -> dto.Currency:
    currency_dto = await currency_dao.get_by_id(currency_id)
    if currency_dto.is_custom and currency_dto.user_id != user.id:
        raise CurrencyNotFound
    return currency_dto


async def add_new_currency(
        currency: dict,
        user: dto.User,
        currency_dao: CurrencyDAO) -> dto.Currency:
    currency_dto = dto.Currency.from_dict(currency)
    currency_dto.user_id = user.id
    currency_dto.is_custom = True
    new_currency_dto = await currency_dao.create(currency_dto)
    await currency_dao.commit()
    return new_currency_dto


async def change_currency(
        currency: dict,
        user: dto.User,
        currency_dao: CurrencyDAO) -> dto.Currency:
    changed_currency_dto = dto.Currency.from_dict(currency)
    currency_dto = await currency_dao.get_by_id(changed_currency_dto.id)
    if currency_dto.user_id != user.id:
        raise CurrencyNotFound

    changed_currency_dto.user_id = user.id
    changed_currency_dto.is_custom = currency_dto.is_custom
    changed_currency_dto = await currency_dao.merge(changed_currency_dto)
    await currency_dao.commit()
    return changed_currency_dto


async def delete_currency(
        currency_id: int,
        user: dto.User,
        currency_dao: CurrencyDAO):
    deleted_currency_id = await currency_dao.delete_by_id(currency_id, user.id)
    if deleted_currency_id is None:
        raise CurrencyNotFound


async def set_base_currency(currency_id: int, user: dto.User, dao: DAO):
    currency = await dao.currency.get_by_id(currency_id)
    if currency.is_custom:
        raise CurrencyCantBeBase

    await dao.user.set_base_currency(user, currency_id)
    await dao.commit()
