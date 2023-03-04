import pytest
from httpx import AsyncClient

from api.v1.dependencies import AuthProvider
from finances.models import dto


@pytest.mark.asyncio
async def test_get_transaction_category(
        transaction_category: dto.TransactionCategory,
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider
):
    token = auth.create_user_token(user)
    resp = await client.get(
        f'/api/v1/transaction/category/{transaction_category.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert resp.is_success

    assert resp.json() == {
        'id': transaction_category.id,
        'title': transaction_category.title,
        'type': transaction_category.type.value
    }


@pytest.mark.asyncio
async def test_add_transaction_category(
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider
):
    token = auth.create_user_token(user)
    category = {
        'title': 'test_expense',
        'type': 'expense'
    }
    resp = await client.post(
        '/api/v1/transaction/category/add',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
        json=category
    )

    assert resp.is_success

    category_resp = resp.json()
    category['id'] = category_resp['id']
    assert category_resp == category


@pytest.mark.asyncio
async def test_change_transaction_category(
        transaction_category: dto.TransactionCategory,
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider
):
    token = auth.create_user_token(user)
    transaction_category.title = 'test change category'
    category_dict = {
        'id': transaction_category.id,
        'title': transaction_category.title,
        'type': transaction_category.type.value
    }
    resp = await client.put(
        '/api/v1/transaction/category/change',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
        json=category_dict
    )

    assert resp.is_success

    assert resp.json() == category_dict


@pytest.mark.asyncio
async def test_delete_transaction_category(
        transaction_category: dto.TransactionCategory,
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider
):
    token = auth.create_user_token(user)
    resp = await client.delete(
        f'/api/v1/transaction/category/{transaction_category.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )

    assert resp.is_success

    resp = await client.get(
        f'/api/v1/transaction/category/{transaction_category.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_all_transaction_categories(
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider
):
    token = auth.create_user_token(user)
    resp = await client.get(
        '/api/v1/transaction/category/all',
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert resp.is_success
    assert len(resp.json()) > 0

    resp = await client.get(
        '/api/v1/transaction/category/all',
        params={'type': 'expense'},
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )

    assert resp.is_success

    is_type = lambda x: [category['type'] == x for category in  # noqa
                         resp.json()]
    assert all(is_type('expense'))

    resp = await client.get(
        '/api/v1/transaction/category/all',
        params={'type': 'income'},
        headers={
            'Authorization': 'Bearer ' + token.access_token}
    )
    assert resp.is_success
    assert all(is_type('income'))
