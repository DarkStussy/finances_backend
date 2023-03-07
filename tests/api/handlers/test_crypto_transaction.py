import pytest
from httpx import AsyncClient

from api.v1.dependencies import AuthProvider
from finances.database.dao import DAO
from finances.models import dto


@pytest.mark.asyncio
async def test_get_crypto_transaction(
        crypto_transaction: dto.CryptoTransaction,
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider
):
    token = auth.create_user_token(user)
    resp = await client.get(
        f'/api/v1/cryptoTransaction/{crypto_transaction.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert resp.is_success
    assert resp.json() == {
        'id': crypto_transaction.id,
        'portfolio_id': str(crypto_transaction.portfolio_id),
        'crypto_asset_id': crypto_transaction.crypto_asset_id,
        'type': crypto_transaction.type.value,
        'amount': float(crypto_transaction.amount),
        'price': float(crypto_transaction.price),
        'created': crypto_transaction.created.isoformat()
    }


@pytest.mark.asyncio
async def test_add_crypto_transaction(
        crypto_portfolio: dto.CryptoPortfolio,
        crypto_asset: dto.CryptoAsset,
        crypto_currency2: dto.CryptoCurrency,
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider,
        dao: DAO
):
    token = auth.create_user_token(user)
    crypto_transaction_dict = {
        'type': 'buy',
        'amount': 10,
        'price': 123,
        'created': '2023-02-19 22:04',
        'portfolio_id': str(crypto_portfolio.id),
        'crypto_asset_id': crypto_asset.id
    }
    resp = await client.post(
        '/api/v1/cryptoTransaction/add',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
        json=crypto_transaction_dict
    )
    assert resp.is_success
    crypto_transaction_dict['created'] = '2023-02-19T22:04:00'
    created_transaction = resp.json()
    crypto_transaction_dict['id'] = created_transaction['id']
    assert created_transaction == crypto_transaction_dict

    del crypto_transaction_dict['id'], crypto_transaction_dict[
        'crypto_asset_id']
    crypto_transaction_dict['crypto_currency_id'] = crypto_currency2.id

    resp = await client.post(
        '/api/v1/cryptoTransaction/add',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
        json=crypto_transaction_dict
    )
    assert resp.is_success
    created_transaction = resp.json()
    crypto_asset_id = created_transaction['crypto_asset_id']
    crypto_transaction_dict['id'] = created_transaction['id']
    created_asset = await dao.crypto_asset.get_by_id(crypto_asset_id)
    assert created_asset.amount == crypto_transaction_dict['amount']
    del crypto_transaction_dict['crypto_currency_id']
    crypto_transaction_dict['crypto_asset_id'] = crypto_asset_id
    assert created_transaction == crypto_transaction_dict


@pytest.mark.asyncio
async def test_change_crypto_transaction(
        crypto_transaction: dto.CryptoTransaction,
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider,
        dao: DAO
):
    token = auth.create_user_token(user)
    crypto_transaction_dict = {
        'type': crypto_transaction.type.value,
        'amount': float(crypto_transaction.amount - 2),
        'price': 123,
        'created': '2023-02-19T22:05:00',
        'id': crypto_transaction.id
    }
    resp = await client.put(
        '/api/v1/cryptoTransaction/change',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
        json=crypto_transaction_dict
    )
    assert resp.is_success
    assert resp.json() == {
        'id': crypto_transaction.id,
        'portfolio_id': str(crypto_transaction.portfolio_id),
        'crypto_asset_id': crypto_transaction.crypto_asset_id,
        'type': crypto_transaction.type.value,
        'amount': float(crypto_transaction.amount - 2),
        'price': 123,
        'created': '2023-02-19T22:05:00'
    }
    crypto_asset_dto = await dao.crypto_asset.get_by_id(
        crypto_transaction.crypto_asset_id)
    assert (crypto_asset_dto.amount - crypto_transaction.amount) == (
            crypto_transaction.amount - 2)


@pytest.mark.asyncio
async def test_delete_crypto_transaction(
        crypto_transaction: dto.CryptoTransaction,
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider
):
    token = auth.create_user_token(user)
    resp = await client.delete(
        f'/api/v1/cryptoTransaction/{crypto_transaction.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert resp.is_success

    resp = await client.get(
        f'/api/v1/cryptoTransaction/{crypto_transaction.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert not resp.is_success
