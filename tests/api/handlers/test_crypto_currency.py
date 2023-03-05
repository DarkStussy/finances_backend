import pytest
from httpx import AsyncClient

from finances.models import dto


@pytest.mark.asyncio
async def test_get_crypto_portfolio(
        client: AsyncClient,
        crypto_currency: dto.CryptoCurrency
):
    resp = await client.get(f'/api/v1/cryptocurrency/{crypto_currency.id}')
    assert resp.is_success

    assert resp.json() == crypto_currency.to_dict()
