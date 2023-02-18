from finances.database.dao.transaction_category import TransactionCategoryDAO
from finances.exceptions.transaction import TransactionCategoryNotFound
from finances.models import dto


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

    return await transaction_category_dao.merge(changed_category_dto)


async def delete_transaction_category(
        category_id: int,
        user: dto.User,
        transaction_category_dao: TransactionCategoryDAO
):
    deleted_category_id = await transaction_category_dao.delete_by_id(
        category_id, user.id)
    if deleted_category_id is None:
        raise TransactionCategoryNotFound
