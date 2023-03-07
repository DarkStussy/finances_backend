import pytest
from httpx import AsyncClient

from api.v1.dependencies import AuthProvider
from finances.models import dto


@pytest.mark.asyncio
async def test_get_crypto_asset(
        crypto_asset: dto.CryptoAsset,
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider
):
    token = auth.create_user_token(user)
    resp = await client.get(
        f'/api/v1/cryptoAsset/{crypto_asset.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert resp.is_success
    assert resp.json() == {
        'id': crypto_asset.id,
        'portfolio_id': str(crypto_asset.portfolio_id),
        'crypto_currency': {
            'id': crypto_asset.crypto_currency.id,
            'name': crypto_asset.crypto_currency.name,
            'code': crypto_asset.crypto_currency.code
        },
        'amount': float(crypto_asset.amount)
    }


@pytest.mark.asyncio
async def test_delete_crypto_asset(
        crypto_asset: dto.CryptoAsset,
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider
):
    token = auth.create_user_token(user)
    resp = await client.delete(
        f'/api/v1/cryptoAsset/{crypto_asset.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert resp.is_success
    resp = await client.get(
        f'/api/v1/cryptoAsset/{crypto_asset.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert not resp.is_success
