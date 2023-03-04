from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from api.v1.dependencies import get_current_user, dao_provider
from api.v1.models.request.transaction_category import \
    TransactionCategoryCreate, TransactionCategoryChange
from api.v1.models.response.transaction_category import \
    TransactionCategoryResponse
from finances.database.dao import DAO
from finances.exceptions.transaction import TransactionCategoryExists, \
    TransactionCategoryNotFound
from finances.models import dto
from finances.models.enums.transaction_type import TransactionType
from finances.services.transaction import add_transaction_category, \
    get_transaction_category_by_id, change_transaction_category, \
    delete_transaction_category


async def get_transaction_category_by_id_route(
        category_id: int,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> TransactionCategoryResponse:
    try:
        category_dto = await get_transaction_category_by_id(
            category_id,
            current_user,
            dao.transaction_category
        )
    except TransactionCategoryNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    else:
        return TransactionCategoryResponse.from_dto(category_dto)


async def get_all_transaction_categories_route(
        transaction_type: TransactionType = Query(default=None, alias='type'),
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> list[TransactionCategoryResponse]:
    return await dao.transaction_category.get_all(
        current_user,
        transaction_type.value if transaction_type else None)


async def add_transaction_category_route(
        category_create: TransactionCategoryCreate,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> TransactionCategoryResponse:
    try:
        category_dto = await add_transaction_category(
            category_create.dict(),
            current_user,
            dao.transaction_category
        )
    except TransactionCategoryExists as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e.message)
    else:
        return TransactionCategoryResponse.from_dto(category_dto)


async def change_transaction_category_route(
        category: TransactionCategoryChange,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> TransactionCategoryResponse:
    try:
        category_dto = await change_transaction_category(
            category.dict(), current_user, dao.transaction_category
        )
    except TransactionCategoryNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    except TransactionCategoryExists as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e.message)
    else:
        return TransactionCategoryResponse.from_dto(category_dto)


async def delete_transaction_category_route(
        category_id: int,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
):
    try:
        await delete_transaction_category(category_id, current_user,
                                          dao.transaction_category)
    except TransactionCategoryNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)

    raise HTTPException(status_code=status.HTTP_200_OK)


def get_transaction_category_router() -> APIRouter:
    router = APIRouter()
    router.add_api_route('/add', add_transaction_category_route,
                         methods=['POST'])
    router.add_api_route('/change', change_transaction_category_route,
                         methods=['PUT'])
    router.add_api_route('/all', get_all_transaction_categories_route,
                         methods=['GET'])
    router.add_api_route('/{category_id}',
                         delete_transaction_category_route,
                         methods=['DELETE'])
    router.add_api_route('/{category_id}',
                         get_transaction_category_by_id_route, methods=['GET'])
    return router
