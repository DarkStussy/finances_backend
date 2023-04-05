from api.v1.dependencies import CurrencyAPI
from finances.database.dao.crypto_currency import CryptoCurrencyDAO
from finances.models import dto


async def get_crypto_currency_price(
        crypto_currency_id: int,
        crypto_currency_dao: CryptoCurrencyDAO,
        currency_api: CurrencyAPI
) -> dto.CryptoCurrencyPrice:
    crypto_currency_dto = await crypto_currency_dao.get_by_id(
        crypto_currency_id)
    price = await currency_api.get_crypto_currency_price(
        crypto_currency_dto.code)
    return dto.CryptoCurrencyPrice(code=crypto_currency_dto.code, price=price)
