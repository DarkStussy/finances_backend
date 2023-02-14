import pytest
from httpx import AsyncClient

from api.v1.dependencies import AuthProvider
from finances.database.dao import DAO
from finances.models import dto


@pytest.mark.asyncio
async def test_signup_user(client: AsyncClient, dao: DAO, auth: AuthProvider):
    username = 'darkstussy'
    password = '123456!Xyz'
    response = await client.post('/api/v1/users/signup', json={
        'username': username,
        'password': password
    })
    assert response.status_code == 200

    created_user = await dao.user.get_by_username_with_password(
        username=username)
    assert auth.verify_password(password, created_user.hashed_password)


@pytest.mark.asyncio
async def test_auth(client: AsyncClient, user: dto.User):
    response = await client.post(
        '/api/v1/auth/login',
        data={'username': user.username, 'password': '12345'},
    )
    assert response.is_success
    response.read()
    access_token = response.json()['access_token']

    response = await client.get(
        '/api/v1/users/me',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.is_success
    response.read()
    actual_user = dto.User.from_dict(response.json())
    assert user == actual_user


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, user: dto.User,
                               auth: AuthProvider):
    token = auth.create_user_token(user)
    resp = await client.put(
        '/api/v1/users/setpassword',
        headers={'Authorization': 'Bearer ' + token.access_token},
        json='test123!T',
    )
    assert resp.is_success

    resp = await client.post(
        '/api/v1/auth/login',
        data={'username': user.username, 'password': '12345'},
    )
    assert not resp.is_success

    resp = await client.post(
        '/api/v1/auth/login',
        data={'username': user.username, 'password': 'test123!T'},
    )
    assert resp.is_success
