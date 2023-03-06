from finances.database.dao import DAO
from finances.database.dao.transaction_category import TransactionCategoryDAO
from finances.exceptions.transaction import TransactionCategoryNotFound, \
    TransactionNotFound, TransactionCantBeChanged
from finances.models import dto
from finances.models.enums.transaction_type import TransactionType

from .asset import get_asset_by_id
from ..database.dao.transaction import TransactionDAO


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
