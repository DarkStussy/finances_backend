import pytest
from httpx import AsyncClient

from api.v1.dependencies import AuthProvider
from finances.database.dao import DAO
from finances.models import dto


@pytest.mark.asyncio
async def test_get_asset(
        asset: dto.Asset,
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider
):
    token = auth.create_user_token(user)
    resp = await client.get(
        f'/api/v1/asset/{asset.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )

    assert resp.is_success

    asset_resp = resp.json()
    asset_dict = {
        'id': str(asset.id),
        'title': asset.title,
        'amount': float(asset.amount),
        'currency': {
            'id': asset.currency_id,
            'name': asset.currency.name,
            'code': asset.currency.code,
            'is_custom': asset.currency.is_custom,
            'rate_to_base_currency': float(
                asset.currency.rate_to_base_currency)
        }
    }
    assert asset_resp == asset_dict


@pytest.mark.asyncio
async def test_create_asset(
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider,
        currency: dto.Currency
):
    token = auth.create_user_token(user)
    new_asset = {
        'title': 'test create asset',
        'currency_id': currency.id,
        'amount': 123
    }
    resp = await client.post(
        '/api/v1/asset/create',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
        json=new_asset
    )

    assert resp.is_success

    asset_resp = resp.json()
    new_asset = new_asset | {
        'id': asset_resp['id'],
        'currency': {
            'id': currency.id,
            'name': currency.name,
            'code': currency.code,
            'is_custom': currency.is_custom,
            'rate_to_base_currency': float(currency.rate_to_base_currency)
        }
    }
    del new_asset['currency_id']
    assert asset_resp == new_asset


@pytest.mark.asyncio
async def test_delete_asset(
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider,
        asset: dto.Asset
):
    token = auth.create_user_token(user)
    resp = await client.delete(
        f'/api/v1/asset/delete/{asset.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )

    assert resp.is_success

    resp = await client.get(
        f'/api/v1/asset/{asset.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_change_asset(
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider,
        dao: DAO,
        asset: dto.Asset
):
    token = auth.create_user_token(user)
    changed_asset = {
        'title': 'test change asset',
        'currency_id': asset.currency_id,
        'amount': 123,
        'id': str(asset.id)
    }
    resp = await client.put(
        f'/api/v1/asset/change',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
        json=changed_asset
    )
    assert resp.is_success

    changed_asset['currency'] = {
        'id': asset.currency.id,
        'name': asset.currency.name,
        'code': asset.currency.code,
        'is_custom': asset.currency.is_custom,
        'rate_to_base_currency': float(asset.currency.rate_to_base_currency)
    }
    del changed_asset['currency_id']
    asset_json = resp.json()
    assert changed_asset == asset_json

    await dao.asset.delete_by_id(asset.id, user.id)


@pytest.mark.asyncio
async def test_delete_asset_currency(
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider,
        dao: DAO,
        asset: dto.Asset
):
    token = auth.create_user_token(user)
    resp = await client.delete(
        f'/api/v1/currency/delete/{asset.currency.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
    )
    assert resp.is_success

    resp = await client.get(
        f'/api/v1/asset/{asset.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert resp.is_success

    asset_json = resp.json()
    asset_dict = {
        'id': str(asset.id),
        'title': asset.title,
        'amount': float(asset.amount),
        'currency': None
    }

    assert asset_dict == asset_json

    await dao.asset.delete_by_id(asset.id, user.id)
