import dataclasses

import pytest
from httpx import AsyncClient

from api.v1.dependencies import AuthProvider
from finances.database.dao import DAO
from finances.models import dto
from tests.fixtures.currency_data import get_test_currency


@pytest.mark.asyncio
async def test_add_currency(
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider):
    token = auth.create_user_token(user)
    currency = get_test_currency()
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
async def test_get_currencies(
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider,
        dao: DAO):
    token = auth.create_user_token(user)
    default_currency_dto = get_test_currency()
    default_currency_dto.name = 'defcur'
    default_currency_dto.code = 'DCR'
    default_currency_dto = await dao.currency.create(default_currency_dto)

    resp = await client.get(
        '/api/v1/currency/all?include_defaults=true',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
    )
    assert resp.is_success
    default_currency_dict = dataclasses.asdict(default_currency_dto)
    default_currency_dict['rate_to_base_currency'] = float(
        default_currency_dto.rate_to_base_currency)
    assert default_currency_dict in resp.json()
