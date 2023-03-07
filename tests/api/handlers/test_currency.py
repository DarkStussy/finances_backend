import dataclasses
from _decimal import Decimal

import pytest
from httpx import AsyncClient

from api.v1.dependencies import AuthProvider
from finances.database.dao import DAO
from finances.models import dto
from tests.fixtures.currency_data import get_test_currency, \
    get_test_base_currency


@pytest.mark.asyncio
async def test_add_currency(
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider):
    token = auth.create_user_token(user)
    currency = get_test_currency()
    currency.rate_to_base_currency = Decimal('0.1')
    resp = await client.post(
        '/api/v1/currency/add',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
        json={
            'name': currency.name,
            'code': currency.code,
            'rate_to_base_currency': float(currency.rate_to_base_currency),
        }
    )

    assert resp.is_success
    currency_id = resp.json().get('id')

    resp = await client.get(
        f'/api/v1/currency/{currency_id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
    )

    assert resp.is_success

    currency_resp = resp.json()
    assert currency.name == currency_resp['name']
    assert currency.code == currency_resp['code']
    assert str(currency.rate_to_base_currency) == \
           str(currency_resp['rate_to_base_currency'])


@pytest.mark.asyncio
async def test_change_currency(
        currency: dto.Currency,
        client: AsyncClient,
        user: dto.User,
        dao: DAO,
        auth: AuthProvider):
    token = auth.create_user_token(user)
    changed_currency = {
        'name': 'changed test',
        'code': 'CTD',
        'rate_to_base_currency': 0.5,
        'id': currency.id
    }
    resp = await client.put(
        '/api/v1/currency/change',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
        json=changed_currency
    )

    assert resp.is_success
    changed_currency['is_custom'] = True
    assert changed_currency == resp.json()

    await dao.currency.delete_by_id(currency.id, user.id)
    await dao.commit()


@pytest.mark.asyncio
async def test_delete_currency(
        currency: dto.Currency,
        auth: AuthProvider,
        user: dto.User,
        client: AsyncClient):
    token = auth.create_user_token(user)
    del_curr = lambda: client.delete(  # noqa
        f'/api/v1/currency/{currency.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
    )
    resp = await del_curr()
    assert resp.is_success
    resp = await del_curr()
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_currency(
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider,
        currency: dto.Currency):
    token = auth.create_user_token(user)
    resp = await client.get(
        f'/api/v1/currency/{currency.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
    )
    assert resp.is_success
    currency_dict = {'name': currency.name,
                     'code': currency.code,
                     'rate_to_base_currency': float(
                         currency.rate_to_base_currency),
                     'is_custom': currency.is_custom,
                     'id': currency.id}
    assert resp.json() == currency_dict


@pytest.mark.asyncio
async def test_get_currencies(
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider,
        currency: dto.Currency):
    token = auth.create_user_token(user)

    resp = await client.get(
        '/api/v1/currency/all?include_defaults=true',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
    )
    assert resp.is_success
    default_currency_dict = dataclasses.asdict(currency)
    default_currency_dict.pop('user_id')
    default_currency_dict['rate_to_base_currency'] = float(
        default_currency_dict['rate_to_base_currency'])
    assert default_currency_dict in resp.json()


@pytest.mark.asyncio
async def test_set_base_currency(
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider,
        dao: DAO
):
    currency = await dao.currency.create(get_test_base_currency())
    await dao.commit()

    token = auth.create_user_token(user)
    resp = await client.put(
        f'/api/v1/currency/baseCurrency/{currency.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
    )

    assert resp.is_success

    resp = await client.get(
        '/api/v1/currency/baseCurrency',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
    )

    assert resp.is_success

    currency_json = resp.json()

    assert {'id': currency.id, 'name': currency.name,
            'code': currency.code, 'is_custom': False,
            'rate_to_base_currency': None} == currency_json
