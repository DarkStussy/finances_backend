from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from api.v1.dependencies import get_current_user, dao_provider
from api.v1.models.request.transaction import TransactionCreate, \
    TransactionChange
from api.v1.models.response.total_result import TotalResult, \
    TransactionsResponse, TotalByAssetResponse
from api.v1.models.response.transaction import TransactionResponse
from finances.database.dao import DAO
from finances.exceptions.asset import AssetNotFound, AssetCantBeDeleted
from finances.exceptions.currency import CurrencyNotFound
from finances.exceptions.transaction import TransactionCategoryNotFound, \
    AddTransactionError, TransactionNotFound, MergeTransactionError, \
    TransactionCantBeChanged, TransactionCantBeDeleted
from finances.models import dto
from finances.models.enums.transaction_type import TransactionType
from finances.services.transaction import add_transaction, \
    get_transaction_by_id, change_transaction, delete_transaction, \
    get_total_transactions_by_period, get_total_categories_by_period, \
    get_totals_by_asset


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
        start_date: date = Query(alias='startDate'),
        end_date: date = Query(alias='endDate'),
        transaction_type: TransactionType = Query(default=None, alias='type'),
        asset_id: UUID = Query(default=None),
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> list[TransactionsResponse]:
    transactions = await dao.transaction.get_all(
        current_user,
        start_date,
        end_date,
        transaction_type.value if transaction_type else None,
        asset_id=asset_id
    )
    if asset_id is None:
        return [
            TransactionsResponse(
                created=item.created,
                transactions=item.transactions
            )
            for item in transactions
        ]
    return transactions


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
    except (CurrencyNotFound, AssetNotFound, TransactionCategoryNotFound) as e:
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
    except (CurrencyNotFound, TransactionNotFound, TransactionCategoryNotFound,
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


async def get_total_transactions_by_period_route(
        start_date: date = Query(alias='startDate'),
        end_date: date = Query(alias='endDate'),
        transaction_type: TransactionType = Query(alias='type'),
        asset_id: UUID = Query(default=None),
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
):
    total = await get_total_transactions_by_period(
        start_date,
        end_date,
        transaction_type,
        asset_id,
        current_user,
        dao
    )
    return TotalResult(total=total)


async def get_total_categories_by_period_route(
        start_date: date = Query(alias='startDate'),
        end_date: date = Query(alias='endDate'),
        transaction_type: TransactionType = Query(alias='type'),
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> list[dto.TotalByCategory]:
    return await get_total_categories_by_period(
        start_date,
        end_date,
        transaction_type,
        current_user,
        dao
    )


async def get_totals_by_asset_route(
        start_date: date = Query(alias='startDate'),
        end_date: date = Query(alias='endDate'),
        asset_id: UUID = Query(default=None),
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
):
    try:
        totals = await get_totals_by_asset(start_date, end_date, asset_id,
                                           current_user, dao)
    except AssetNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    return TotalByAssetResponse(
        asset_id=asset_id,
        total_income=totals.income,
        total_expense=totals.expense
    )


def get_transaction_router() -> APIRouter:
    router = APIRouter()
    router.add_api_route('/add', add_transaction_route, methods=['POST'])
    router.add_api_route('/change', change_transaction_route, methods=['PUT']),
    router.add_api_route('/all', get_all_transactions_route, methods=['GET'])
    router.add_api_route('/totalByPeriod',
                         get_total_transactions_by_period_route,
                         methods=['GET'])
    router.add_api_route('/totalCategoriesByPeriod',
                         get_total_categories_by_period_route,
                         methods=['GET'])
    router.add_api_route('/totalsByAsset', get_totals_by_asset_route,
                         methods=['GET'])
    router.add_api_route('/{transaction_id}', delete_transaction_route,
                         methods=['DELETE'])
    router.add_api_route('/{transaction_id}', get_transaction_by_id_route,
                         methods=['GET'])
    return router
