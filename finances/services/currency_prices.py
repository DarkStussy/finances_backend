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


async def get_crypto_currencies_prices(
        crypto_currencies: list[int],
        crypto_currency_dao: CryptoCurrencyDAO,
        currency_api: CurrencyAPI
) -> list[dto.CryptoCurrencyPrice]:
    crypto_currencies = await crypto_currency_dao.get_all(ids=crypto_currencies)
    if not crypto_currencies:
        return []

    crypto_codes = [crypto_currency.code for crypto_currency in crypto_currencies]
    currencies_prices = await currency_api.get_crypto_currency_prices(crypto_codes)
    return [dto.CryptoCurrencyPrice(code=code.replace('USDT', ''), price=price) for code, price in
            currencies_prices.items()]
