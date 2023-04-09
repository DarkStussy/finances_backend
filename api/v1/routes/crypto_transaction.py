from fastapi import APIRouter, Depends
from starlette import status
from starlette.exceptions import HTTPException

from api.v1.dependencies import get_current_user, dao_provider
from api.v1.models.request.crypto_transaction import CryptoTransactionCreate, \
    CryptoTransactionChange
from api.v1.models.response.crypto_transaction import CryptoTransactionResponse
from finances.database.dao import DAO
from finances.exceptions.crypto_asset import AddCryptoAssetError, \
    CryptoAssetNotFound, MergeCryptoAssetError
from finances.exceptions.crypto_portfolio import CryptoPortfolioNotFound
from finances.exceptions.crypto_transaction import AddCryptoTransactionError, \
    CryptoTransactionNotFound, MergeCryptoTransactionError
from finances.models import dto
from finances.services.crypto_transaction import add_crypto_transaction, \
    get_crypto_transaction_by_id, change_crypto_transaction, \
    delete_crypto_transaction


async def get_crypto_transaction_by_id_route(
        crypto_transaction_id: int,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> CryptoTransactionResponse:
    try:
        crypto_transaction_dto = await get_crypto_transaction_by_id(
            crypto_transaction_id,
            current_user,
            dao.crypto_transaction
        )
    except CryptoTransactionNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    else:
        return CryptoTransactionResponse.from_dto(crypto_transaction_dto)


async def get_all_crypto_transactions_route(
        crypto_asset_id: int,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> list[CryptoTransactionResponse]:
    return await dao.crypto_transaction.get_all_by_crypto_asset(
        crypto_asset_id=crypto_asset_id,
        user_id=current_user.id
    )


async def add_crypto_transaction_route(
        crypto_transaction: CryptoTransactionCreate,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> CryptoTransactionResponse:
    try:
        crypto_transaction_dto = await add_crypto_transaction(
            crypto_transaction.dict(),
            current_user,
            dao
        )
    except (AddCryptoAssetError, MergeCryptoAssetError,
            AddCryptoTransactionError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e.message)
    except (CryptoAssetNotFound, CryptoPortfolioNotFound) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    else:
        return CryptoTransactionResponse.from_dto(crypto_transaction_dto)


async def change_crypto_transaction_route(
        crypto_transaction: CryptoTransactionChange,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
) -> CryptoTransactionResponse:
    try:
        crypto_transaction_dto = await change_crypto_transaction(
            crypto_transaction.dict(),
            current_user,
            dao
        )
    except CryptoTransactionNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    except (MergeCryptoAssetError, MergeCryptoTransactionError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e.message)
    else:
        return CryptoTransactionResponse.from_dto(crypto_transaction_dto)


async def delete_crypto_transaction_route(
        crypto_transaction_id: int,
        current_user: dto.User = Depends(get_current_user),
        dao: DAO = Depends(dao_provider)
):
    try:
        await delete_crypto_transaction(
            crypto_transaction_id,
            current_user,
            dao
        )
    except CryptoTransactionNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    raise HTTPException(status_code=status.HTTP_200_OK)


def get_crypto_transaction_router() -> APIRouter:
    router = APIRouter()
    router.add_api_route('/add', add_crypto_transaction_route,
                         methods=['POST'])
    router.add_api_route('/change', change_crypto_transaction_route,
                         methods=['PUT'])
    router.add_api_route('/all', get_all_crypto_transactions_route,
                         methods=['GET'])
    router.add_api_route('/{crypto_transaction_id}',
                         delete_crypto_transaction_route,
                         methods=['DELETE'])
    router.add_api_route('/{crypto_transaction_id}',
                         get_crypto_transaction_by_id_route,
                         methods=['GET'])
    return router
