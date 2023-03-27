import logging
from _decimal import Decimal
from dataclasses import dataclass

from httpx import AsyncClient


def currency_api_provider():
    raise NotImplementedError


class CantGetPrice(Exception):
    def __init__(self):
        super().__init__('Unable to get price')


@dataclass(frozen=True)
class FCSAPI:
    access_key: str
    base_url: str = 'https://fcsapi.com/api-v3/forex'


@dataclass(frozen=True)
class BinanceAPI:
    base_url: str = 'https://api.binance.com/api/v3/'


class CurrencyAPI:
    def __init__(self, access_key: str, client: AsyncClient):
        self._client = client
        self.fcsapi = FCSAPI(access_key=access_key)
        self.binance_api = BinanceAPI()

    async def get_currency_prices(
            self,
            currencies: set[str],
            base_currency: str = 'USD'
    ) -> dict[str, Decimal]:
        response = await self._client.get(
            f'{self.fcsapi.base_url}/latest',
            params={
                'symbol': ','.join(
                    f'{base_currency}/{currency}' for currency in currencies),
                'access_key': self.fcsapi.access_key
            },
            timeout=10
        )
        response_json = response.json()
        status = response_json.get('status', False)
        if not status:
            logging.error(
                f'[FSCAPI:get_currency_prices] response: {response_json}')
            raise CantGetPrice

        return {currency['s'].split('/')[-1]: Decimal(currency['c']) for
                currency in response_json['response']}

    async def get_crypto_currency_price(self, crypto_code: str) -> Decimal:
        response = await self._client.get(
            f'{self.binance_api.base_url}ticker/price?symbol={crypto_code}BUSD'
        )
        crypto_currency = response.json()
        if response.status_code != 200:
            logging.error(
                f'[BinanceAPI:get_crypto_currency_price] response: '
                f'{crypto_currency}')
            raise CantGetPrice
        return crypto_currency['price']

    async def get_crypto_currency_prices(self, crypto_codes: list[str]) \
            -> dict[str, Decimal]:
        response = await self._client.get(
            self.binance_api.base_url + 'ticker/price?symbols',
            params={
                'symbols': '[' + ','.join(
                    f'"{code}BUSD"' for code in crypto_codes) + ']'
            }
        )
        prices = response.json()
        if response.status_code != 200:
            logging.error(
                f'[BinanceAPI:get_crypto_currency_prices] response: {prices}')
            raise CantGetPrice

        return {price['symbol']: Decimal(price['price']) for price in prices}
