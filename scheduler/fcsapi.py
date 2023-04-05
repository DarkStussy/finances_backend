from decimal import Decimal
from dataclasses import dataclass

from httpx import AsyncClient

from finances.models import dto


@dataclass(frozen=True)
class FCSAPI:
    access_key: str
    base_url: str = 'https://fcsapi.com/api-v3/forex'


class FCSClient:
    def __init__(self, access_key: str, client: AsyncClient):
        self._client = client
        self.fcsapi = FCSAPI(access_key=access_key)

    async def get_all_prices(self):
        response = await self._client.get(
            f'{self.fcsapi.base_url}/latest',
            params={
                'symbol': 'all_forex',
                'access_key': self.fcsapi.access_key
            },
            timeout=10
        )
        response_json = response.json()
        status = response_json.get('status', False)
        if not status:
            return

        currency_prices: list[dto.CurrencyPrice] = []
        for currency in response_json['response']:
            base, quote = currency['s'].split('/')
            currency_prices.append(
                dto.CurrencyPrice(
                    base=base,
                    quote=quote,
                    price=Decimal(currency['c'])
                )
            )
        return currency_prices
