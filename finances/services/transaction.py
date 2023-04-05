from datetime import date
from uuid import UUID

from finances.database.dao import DAO
from finances.database.dao.transaction_category import TransactionCategoryDAO
from finances.exceptions.transaction import TransactionCategoryNotFound, \
    TransactionNotFound, TransactionCantBeChanged
from finances.models import dto
from finances.models.enums.transaction_type import TransactionType

from .asset import get_asset_by_id
from ..database.dao.transaction import TransactionDAO
from ..exceptions.asset import AssetNotFound
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
    exiting_category_dto = \
        await transaction_category_dao.get_by_title_and_type(
            title=category_dto.title,
            transaction_type=category_dto.type,
            user_id=user.id
        )
    if exiting_category_dto is not None and exiting_category_dto.deleted:
        await transaction_category_dao.restore(exiting_category_dto.id)
        await transaction_category_dao.commit()
        exiting_category_dto.deleted = False
        return exiting_category_dto

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
    transaction_dto.category_id = category_id
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
        asset_id: UUID | None,
        user: dto.User,
        dao: DAO
) -> float:
    currencies_amount = await dao.transaction.get_total_by_period(
        user,
        start_date,
        end_date,
        transaction_type.value,
        asset_id
    )
    if not currencies_amount:
        return 0

    base_currency = await dao.user.get_base_currency(user)
    base_currency_code = getattr(base_currency, 'code', 'USD')
    currencies_codes = [
        currency for currency, value in currencies_amount.items()
        if value[0] is None and currency != base_currency_code
    ]
    prices = await dao.currency_price.get_prices(
        base_currency_code, currencies_codes)
    total = 0

    for code, (custom_rate, amount) in currencies_amount.items():
        if custom_rate is not None:
            total += amount / custom_rate
            continue

        currency_price = prices.get(code)
        if currency_price is None:
            rate = 1
        else:
            rate = currency_price.price

        total += amount / rate

    return round(total, 2)


async def get_total_categories_by_period(
        start_date: date,
        end_date: date,
        transaction_type: TransactionType,
        user: dto.User,
        dao: DAO
) -> list[TotalByCategory]:
    totals_cat_and_cur = await dao.transaction.get_total_categories_by_period(
        user, start_date, end_date, transaction_type.value
    )
    if not totals_cat_and_cur:
        return []
    currencies_codes = [
        total_cat_and_cur.currency_code for total_cat_and_cur in
        totals_cat_and_cur if total_cat_and_cur.rate_to_base_currency is None
    ]

    base_currency = await dao.user.get_base_currency(user)
    prices = await dao.currency_price.get_prices(
        getattr(base_currency, 'code', 'USD'), currencies_codes)

    totals_by_category = {}
    for total_cat_and_cur in totals_cat_and_cur:
        category = totals_by_category.get(total_cat_and_cur.category)
        rate = total_cat_and_cur.rate_to_base_currency
        if rate is None:
            currency_price = prices.get(total_cat_and_cur.currency_code)
            if currency_price is None:
                rate = 1
            else:
                rate = currency_price.price

        total = total_cat_and_cur.total / rate
        if category is None:
            totals_by_category[
                total_cat_and_cur.category] = total
        else:
            totals_by_category[
                total_cat_and_cur.category] += total

    return [TotalByCategory(category=cat, type=transaction_type.value,
                            total=round(total, 2))
            for cat, total in totals_by_category.items()]


async def get_totals_by_asset(
        start_date: date,
        end_date: date,
        asset_id: UUID | None,
        user: dto.User,
        dao: DAO
) -> dto.TotalsByAsset:
    asset_dto = await dao.asset.get_by_id(asset_id)
    if asset_dto.user_id != user.id:
        raise AssetNotFound

    return await dao.transaction.get_totals_by_asset(asset_id, start_date,
                                                     end_date)
