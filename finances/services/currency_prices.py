from _decimal import Decimal

from api.v1.dependencies import CurrencyAPI
from finances.database.dao.crypto_currency import CryptoCurrencyDAO
from finances.models import dto


async def get_prices(
        base_currency: dto.Currency | None,
        currencies_codes: set[str],
        currency_api: CurrencyAPI
) -> dict[str, Decimal]:
    if base_currency is None:
        base_currency_code = 'USD'
    else:
        base_currency_code = base_currency.code

    try:
        currencies_codes.remove(base_currency_code)
    except KeyError:
        pass
    if len(currencies_codes) == 0:
        prices = {}
    else:
        prices = await currency_api.get_currency_prices(currencies_codes,
                                                        base_currency_code)
    prices[base_currency_code] = Decimal('1')
    return prices


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
