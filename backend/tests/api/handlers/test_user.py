import pytest
from httpx import AsyncClient

from backend.api.v1.dependencies import AuthProvider
from backend.finances.database.dao import DAO
from backend.finances.models import dto


@pytest.mark.asyncio
async def test_signup_user(client: AsyncClient, dao: DAO, auth: AuthProvider):
    username = 'darkstussy'
    password = '123456!Xyz'
    response = await client.post('/api/v1/user/signup', json={
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
        '/api/v1/user/me',
        headers={'Authorization': 'Bearer ' + access_token},
    )
    assert response.is_success
    response.read()
    actual_user = dto.User.from_dict(response.json())
    user.id = str(user.id)
    assert user == actual_user


@pytest.mark.asyncio
async def test_change_username(client: AsyncClient,
                               user: dto.User,
                               auth: AuthProvider,
                               dao: DAO):
    token = auth.create_user_token(user)
    new_username = 'test12345'
    resp = await client.put(
        '/api/v1/user/setusername',
        headers={'Authorization': 'Bearer ' + token.access_token},
        json={'username': new_username},
    )
    assert resp.is_success

    user.username = new_username
    token = auth.create_user_token(user)
    resp = await client.get(
        '/api/v1/user/me',
        headers={'Authorization': 'Bearer ' + token.access_token},
    )
    assert resp.is_success
    user_json = resp.json()
    assert user_json['username'] == user.username

    await dao.user.delete_by_id(user.id)
    await dao.commit()


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, user: dto.User,
                               auth: AuthProvider):
    token = auth.create_user_token(user)
    resp = await client.put(
        '/api/v1/user/setpassword',
        headers={'Authorization': 'Bearer ' + token.access_token},
        json={'password': 'test123!T'},
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
