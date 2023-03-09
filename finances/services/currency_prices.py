from _decimal import Decimal

from api.v1.dependencies import FCSAPI
from finances.models import dto


async def get_prices(
        base_currency: dto.Currency | None,
        currencies_codes: set[str],
        fcsapi: FCSAPI
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
        prices = await fcsapi.get_prices(currencies_codes, base_currency_code)
    prices[base_currency_code] = Decimal('1')
    return prices
