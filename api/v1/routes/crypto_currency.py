from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from api.v1.dependencies import dao_provider, CurrencyAPI, \
    currency_api_provider
from api.v1.dependencies.currency_api import CantGetPrice
from finances.database.dao import DAO
from finances.exceptions.crypto_currency import CryptoCurrencyNotFound
from finances.models import dto
from finances.services.currency_prices import get_crypto_currency_price


async def get_crypto_currency_by_id_route(
        crypto_currency_id: int,
        dao: DAO = Depends(dao_provider)
) -> dto.CryptoCurrency:
    try:
        crypto_currency_dto = await dao.crypto_currency.get_by_id(
            crypto_currency_id)
    except CryptoCurrencyNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    else:
        return crypto_currency_dto


async def get_all_crypto_currencies_route(
        search: str = Query(default=None, description='Search by crypto code'),
        dao: DAO = Depends(dao_provider)
) -> list[dto.CryptoCurrency]:
    return await dao.crypto_currency.get_all(search)


async def get_crypto_currency_price_route(
        crypto_currency_id: int,
        dao: DAO = Depends(dao_provider),
        currency_api: CurrencyAPI = Depends(currency_api_provider)
) -> dto.CryptoCurrencyPrice:
    try:
        return await get_crypto_currency_price(
            crypto_currency_id,
            dao.crypto_currency,
            currency_api
        )
    except CryptoCurrencyNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.message)
    except CantGetPrice:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='Unable to calculate price')


# async def add_crypto_currencies_route(
#         dao: DAO = Depends(dao_provider)
# ):
#     async with AsyncClient() as async_client:
#         response = await async_client.get(
#             url='https://www.binance.com/bapi/asset/v2/public/'
#                 'asset/asset/get-all-asset'
#         )
#         response = response.json()
#         for crypto_currency in response['data']:
#             try:
#                 await dao.crypto_currency.create(
#                     dto.CryptoCurrency(
#                         id=None,
#                         name=crypto_currency['assetName'],
#                         code=crypto_currency['assetCode']
#                     )
#                 )
#             except CryptoCurrencyExists:
#                 print(crypto_currency['assetName'],
#                       crypto_currency['assetCode'])
#         await dao.commit()


def get_crypto_currency_router() -> APIRouter:
    router = APIRouter()
    router.add_api_route('/all', get_all_crypto_currencies_route,
                         methods=['GET'])
    router.add_api_route('/price/{crypto_currency_id}',
                         get_crypto_currency_price_route, methods=['GET'])
    router.add_api_route('/{crypto_currency_id}',
                         get_crypto_currency_by_id_route,
                         methods=['GET'])
    return router
