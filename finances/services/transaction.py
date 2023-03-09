from datetime import date

from api.v1.dependencies import CurrencyAPI
from finances.database.dao import DAO
from finances.database.dao.transaction_category import TransactionCategoryDAO
from finances.exceptions.transaction import TransactionCategoryNotFound, \
    TransactionNotFound, TransactionCantBeChanged
from finances.models import dto
from finances.models.enums.transaction_type import TransactionType

from .asset import get_asset_by_id
from .currency_prices import get_prices
from ..database.dao.transaction import TransactionDAO
from ..models.dto import TotalByCategory


# transaction category
async def get_transaction_category_by_id(
        category_id: int,
        user: dto.User,
        transaction_category_dao: TransactionCategoryDAO
):
    category_dto = await transaction_category_dao.get_by_id(category_id)
    if category_dto.user_id != user.id:
        raise TransactionCategoryNotFound

    return category_dto


async def add_transaction_category(
        category: dict,
        user: dto.User,
        transaction_category_dao: TransactionCategoryDAO
) -> dto.TransactionCategory:
    category_dto = dto.TransactionCategory.from_dict(category)
    category_dto.user_id = user.id
    category_dto = await transaction_category_dao.create(category_dto)
    await transaction_category_dao.commit()
    return category_dto


async def change_transaction_category(
        category: dict,
        user: dto.User,
        transaction_category_dao: TransactionCategoryDAO
):
    changed_category_dto = dto.TransactionCategory.from_dict(category)
    category_dto = await transaction_category_dao.get_by_id(
        changed_category_dto.id)
    if category_dto is None or category_dto.user_id != user.id:
        raise TransactionCategoryNotFound

    changed_category_dto.user_id = user.id
    changed_category_dto = await transaction_category_dao.merge(
        changed_category_dto)
    await transaction_category_dao.commit()
    return changed_category_dto


async def delete_transaction_category(
        category_id: int,
        user: dto.User,
        transaction_category_dao: TransactionCategoryDAO
):
    category_dto = await transaction_category_dao.get_by_id(
        category_id)
    if category_dto.user_id != user.id:
        raise TransactionCategoryNotFound

    category_dto.deleted = True
    await transaction_category_dao.merge(category_dto)
    await transaction_category_dao.commit()


# transaction

async def get_transaction_by_id(
        transaction_id: int,
        user: dto.User,
        transaction_dao: TransactionDAO
) -> dto.Transaction:
    transaction_dto = await transaction_dao.get_by_id(transaction_id)
    if transaction_dto.user_id != user.id:
        raise TransactionNotFound

    return transaction_dto


async def add_transaction(
        transaction: dict,
        user: dto.User,
        dao: DAO
) -> dto.Transaction:
    asset_id = transaction['asset_id']
    category_id = transaction['category_id']
    asset_dto = await get_asset_by_id(asset_id, user, dao.asset)
    category_dto = await get_transaction_category_by_id(
        category_id, user, dao.transaction_category)

    transaction_dto = dto.Transaction(
        id=None,
        user_id=user.id,
        asset_id=asset_dto.id,
        category_id=category_dto.id,
        amount=transaction['amount'],
        created=transaction['created']
    )
    transaction_dto = await dao.transaction.create(transaction_dto)

    if category_dto.type == TransactionType.INCOME:
        asset_dto.amount += transaction_dto.amount
    elif category_dto.type == TransactionType.EXPENSE:
        asset_dto.amount -= transaction_dto.amount

    await dao.asset.merge(asset_dto)
    await dao.commit()

    transaction_dto.asset = asset_dto
    currency_dto = await dao.currency.get_by_id(
        transaction_dto.asset.currency_id)
    transaction_dto.asset.currency = currency_dto
    transaction_dto.category = category_dto
    return transaction_dto


async def change_transaction(
        transaction: dict,
        user: dto.User,
        dao: DAO
) -> dto.Transaction:
    asset_id = transaction['asset_id']
    category_id = transaction['category_id']
    amount = transaction['amount']
    created = transaction['created']
    transaction_id = transaction['id']

    transaction_dto = await dao.transaction.get_by_id(transaction_id)
    if transaction_dto.user_id != user.id:
        raise TransactionNotFound

    category_dto = await get_transaction_category_by_id(
        category_id, user, dao.transaction_category) if \
        transaction_dto.category.id != category_id else \
        transaction_dto.category

    if category_dto.type != transaction_dto.category.type or all(
            [
                transaction_dto.asset_id == asset_id,
                transaction_dto.category_id == category_id,
                transaction_dto.amount == amount,
                transaction_dto.created == created
            ]
    ):
        raise TransactionCantBeChanged(
            'Transaction category cannot be changed')

    if transaction_dto.asset_id != asset_id:
        asset_dto = await get_asset_by_id(asset_id, user, dao.asset)
        if transaction_dto.category.type == TransactionType.INCOME:
            transaction_dto.asset.amount -= transaction_dto.amount
        elif transaction_dto.category.type == TransactionType.EXPENSE:
            transaction_dto.asset.amount += transaction_dto.amount

        if category_dto.type == TransactionType.INCOME:
            asset_dto.amount += amount
        elif category_dto.type == TransactionType.EXPENSE:
            asset_dto.amount -= amount

        await dao.asset.merge(transaction_dto.asset)
        await dao.asset.merge(asset_dto)
    else:
        asset_dto = transaction_dto.asset
        if category_dto.type == TransactionType.INCOME:
            asset_dto.amount = asset_dto.amount - transaction_dto.amount \
                               + amount
        elif category_dto.type == TransactionType.EXPENSE:
            asset_dto.amount = asset_dto.amount + transaction_dto.amount \
                               - amount

        await dao.asset.merge(asset_dto)

    transaction_dto.asset_id = asset_id
    transaction_dto.category = category_id
    transaction_dto.amount = amount
    transaction_dto.created = created

    await dao.transaction.merge(transaction_dto)
    await dao.commit()

    transaction_dto.asset = asset_dto
    transaction_dto.category = category_dto
    return transaction_dto


async def delete_transaction(
        transaction_id: int,
        user: dto.User,
        dao: DAO
):
    transaction_dto = await dao.transaction.delete_by_id(transaction_id,
                                                         user.id)
    if transaction_dto is None:
        raise TransactionNotFound

    category = await dao.transaction_category.get_by_id(
        transaction_dto.category_id)
    transaction_dto.category = category
    amount = transaction_dto.amount
    if transaction_dto.category.type == TransactionType.INCOME:
        amount = -amount

    await dao.asset.update_amount(
        amount,
        transaction_dto.asset_id,
        user.id
    )
    await dao.commit()


async def get_total_transactions_by_period(
        start_date: date,
        end_date: date,
        transaction_type: TransactionType,
        user: dto.User,
        currency_api: CurrencyAPI,
        dao: DAO
) -> float:
    currencies_amount = await dao.transaction.get_total_by_period(
        user,
        start_date,
        end_date,
        transaction_type.value
    )
    if not currencies_amount:
        return 0

    currencies_codes = set(
        [currency for currency, value in currencies_amount.items() if
         value[0] is None])
    base_currency = await dao.user.get_base_currency(user)
    prices = await get_prices(base_currency, currencies_codes, currency_api)

    return round(sum([
        value[1] / prices[code] if value[0] is None else value[1] / value[0]
        for code, value in currencies_amount.items()
    ]), 2)


async def get_total_categories_by_period(
        start_date: date,
        end_date: date,
        transaction_type: TransactionType,
        user: dto.User,
        currency_api: CurrencyAPI,
        dao: DAO
) -> list[TotalByCategory]:
    totals_cat_and_cur = await dao.transaction.get_total_categories_by_period(
        user, start_date, end_date, transaction_type.value
    )
    if not totals_cat_and_cur:
        return []
    currencies_codes = set(
        total_cat_and_cur.currency_code for total_cat_and_cur in
        totals_cat_and_cur if total_cat_and_cur.rate_to_base_currency is None)

    base_currency = await dao.user.get_base_currency(user)
    prices = await get_prices(base_currency, currencies_codes, currency_api)
    totals_by_category = {}
    for total_cat_and_cur in totals_cat_and_cur:
        category = totals_by_category.get(total_cat_and_cur.category)
        rate = total_cat_and_cur.rate_to_base_currency \
            if total_cat_and_cur.rate_to_base_currency \
            else prices[total_cat_and_cur.currency_code]
        total = total_cat_and_cur.total / rate
        if category is None:
            totals_by_category[
                total_cat_and_cur.category] = total
        else:
            totals_by_category[
                total_cat_and_cur.category] += total

    return sorted([TotalByCategory(category=k, type=transaction_type.value,
                                   total=round(v, 2))
                   for k, v in totals_by_category.items()],
                  key=lambda x: x.total, reverse=True)
