from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from backend.api.v1.dependencies import get_current_user, dao_provider
from backend.api.v1.models.request.transaction import TransactionCreate, \
    TransactionChange
from backend.api.v1.models.response.transaction import TransactionResponse
from backend.finances.database.dao import DAO
from backend.finances.exceptions.asset import AssetNotFound, AssetCantBeDeleted
from backend.finances.exceptions.transaction import \
    TransactionCategoryNotFound, \
    AddTransactionError, TransactionNotFound, MergeTransactionError, \
    TransactionCantBeChanged, TransactionCantBeDeleted
from backend.finances.models import dto
from backend.finances.models.enums.transaction_type import TransactionType
from backend.finances.services.transaction import add_transaction, \
    get_transaction_by_id, change_transaction, delete_transaction


async def get_transaction_by_id_route(
        transaction_id: int,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> TransactionResponse:
    try:
        transaction_dto = await get_transaction_by_id(transaction_id,
                                                      current_user,
                                                      dao.transaction)
    except TransactionNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    else:
        return TransactionResponse.from_dto(transaction_dto)


async def get_all_transactions_route(
        transaction_type: TransactionType = Query(default=None, alias='type'),
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> list[TransactionResponse]:
    return await dao.transaction.get_all(
        current_user,
        transaction_type.value if transaction_type else None
    )


async def add_transaction_route(
        transaction: TransactionCreate,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> TransactionResponse:
    try:
        transaction_dto = await add_transaction(
            transaction.dict(),
            current_user,
            dao
        )
    except (AssetNotFound, TransactionCategoryNotFound) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    except AddTransactionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e.message)
    else:
        return TransactionResponse.from_dto(transaction_dto)


async def change_transaction_route(
        transaction: TransactionChange,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> TransactionResponse:
    try:
        transaction_dto = await change_transaction(
            transaction.dict(),
            current_user, dao
        )
    except (MergeTransactionError, TransactionCantBeChanged) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e.message)
    except (TransactionNotFound, TransactionCategoryNotFound,
            AssetNotFound) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    else:
        return TransactionResponse.from_dto(transaction_dto)


async def delete_transaction_route(
        transaction_id: int,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
):
    try:
        await delete_transaction(transaction_id, current_user, dao)
    except TransactionNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    except (AssetCantBeDeleted, TransactionCantBeDeleted) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e.message)
    else:
        raise HTTPException(status_code=status.HTTP_200_OK)


def get_transaction_router() -> APIRouter:
    router = APIRouter()
    router.add_api_route('/add', add_transaction_route, methods=['POST'])
    router.add_api_route('/change', change_transaction_route, methods=['PUT']),
    router.add_api_route('/delete/{transaction_id}', delete_transaction_route,
                         methods=['DELETE'])
    router.add_api_route('/all', get_all_transactions_route, methods=['GET'])
    router.add_api_route('/{transaction_id}', get_transaction_by_id_route,
                         methods=['GET'])
    return router
