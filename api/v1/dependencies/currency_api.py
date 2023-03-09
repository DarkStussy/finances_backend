import logging
from _decimal import Decimal

from httpx import AsyncClient


def currency_api_provider():
    raise NotImplementedError


class CantGetPrices(Exception):
    def __init__(self):
        super().__init__('Unable to get prices')


class FCSAPI:
    def __init__(self, access_key: str, client: AsyncClient):
        self._base_url = 'https://fcsapi.com/api-v3/forex'
        self._access_key = access_key
        self._client = client

    async def get_prices(
            self,
            currencies: set[str],
            base_currency: str = 'USD'
    ) -> dict[str, Decimal]:
        response = await self._client.get(
            f'{self._base_url}/latest',
            params={
                'symbol': ','.join(
                    f'{base_currency}/{currency}' for currency in currencies),
                'access_key': self._access_key
            }
        )
        response_json = response.json()
        status = response_json.get('status', False)
        if not status:
            logging.error(f'[FSCAPI:get_prices] response: {response_json}')
            raise CantGetPrices

        return {currency['s'].split('/')[-1]: Decimal(currency['c']) for
                currency in response_json['response']}
