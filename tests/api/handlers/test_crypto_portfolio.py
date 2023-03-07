import pytest
from httpx import AsyncClient
from sqlalchemy import update

from api.v1.dependencies import AuthProvider
from finances.database.dao import DAO
from finances.database.models import UserConfiguration
from finances.models import dto


@pytest.mark.asyncio
async def test_get_crypto_portfolio(
        client: AsyncClient,
        user: dto.User,
        crypto_portfolio: dto.CryptoPortfolio,
        auth: AuthProvider
):
    token = auth.create_user_token(user)

    resp = await client.get(
        f'api/v1/cryptoportfolio/{crypto_portfolio.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert resp.is_success

    assert resp.json() == {
        'id': str(crypto_portfolio.id),
        'title': crypto_portfolio.title
    }


@pytest.mark.asyncio
async def test_add_crypto_portfolio(
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider
):
    token = auth.create_user_token(user)

    resp = await client.post(
        'api/v1/cryptoportfolio/add',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
        json={
            'title': 'test add cp'
        }
    )
    assert resp.is_success
    resp_dict = resp.json()
    assert resp_dict == {
        'id': resp_dict['id'],
        'title': 'test add cp'
    }


@pytest.mark.asyncio
async def test_change_crypto_portfolio(
        client: AsyncClient,
        user: dto.User,
        crypto_portfolio: dto.CryptoPortfolio,
        auth: AuthProvider
):
    token = auth.create_user_token(user)

    request = lambda x: client.put(  # noqa
        'api/v1/cryptoportfolio/change',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
        json={
            'id': str(crypto_portfolio.id),
            'title': x
        }
    )
    resp = await request('test change cp')
    assert resp.is_success
    assert resp.json() == {
        'id': str(crypto_portfolio.id),
        'title': 'test change cp'
    }
    resp = await request('test add cp')
    assert not resp.is_success
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_delete_crypto_portfolio(
        client: AsyncClient,
        user: dto.User,
        crypto_portfolio: dto.CryptoPortfolio,
        auth: AuthProvider
):
    token = auth.create_user_token(user)
    resp = await client.delete(
        f'api/v1/cryptoportfolio/{crypto_portfolio.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert resp.is_success

    resp = await client.get(
        f'api/v1/cryptoportfolio/{crypto_portfolio.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert not resp.is_success
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_base_portfolio(
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider,
        crypto_portfolio: dto.CryptoPortfolio,
):
    token = auth.create_user_token(user)
    resp = await client.get(
        'api/v1/cryptoportfolio/baseCryptoportfolio',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert resp.is_success
    assert resp.json() == {
        'id': str(crypto_portfolio.id),
        'title': crypto_portfolio.title
    }


@pytest.mark.asyncio
async def test_set_base_portfolio(
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider,
        crypto_portfolio: dto.CryptoPortfolio,
        dao: DAO
):
    token = auth.create_user_token(user)
    await dao.session.execute(update(UserConfiguration).where(
        UserConfiguration.id == user.id).values(base_crypto_portfolio_id=None))
    await dao.commit()

    resp = await client.get(
        'api/v1/cryptoportfolio/baseCryptoportfolio',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert resp.status_code == 404

    resp = await client.put(
        f'api/v1/cryptoportfolio/baseCryptoportfolio/{crypto_portfolio.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert resp.is_success
    base_portfolio = await dao.user.get_base_crypto_portfolio(user)
    assert base_portfolio == crypto_portfolio
