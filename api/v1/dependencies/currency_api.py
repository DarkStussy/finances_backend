import logging
from decimal import Decimal
from dataclasses import dataclass

from httpx import AsyncClient


def currency_api_provider():
    raise NotImplementedError


class CantGetPrice(Exception):
    def __init__(self):
        super().__init__('Unable to get price')


@dataclass(frozen=True)
class BinanceAPI:
    base_url: str = 'https://api.binance.com/api/v3/'


class CurrencyAPI:
    def __init__(self, client: AsyncClient):
        self._client = client
        self.binance_api = BinanceAPI()

    async def get_crypto_currency_price(self, crypto_code: str) -> Decimal:
        response = await self._client.get(
            f'{self.binance_api.base_url}ticker/price?symbol={crypto_code}BUSD'
        )
        crypto_currency = response.json()
        if response.status_code != 200:
            response = await self._client.get(
                f'{self.binance_api.base_url}ticker/price?symbol={crypto_code}USDT'
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
