from _decimal import Decimal

import pytest
from httpx import AsyncClient

from api.v1.dependencies import AuthProvider
from finances.database.dao import DAO
from finances.exceptions.transaction import TransactionNotFound
from finances.models import dto


@pytest.mark.asyncio
async def test_get_transaction(
        transaction: dto.Transaction,
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider
):
    token = auth.create_user_token(user)
    resp = await client.get(
        f'/api/v1/transaction/{transaction.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
    )
    assert resp.is_success
    transaction_dict = resp.json()
    assert transaction_dict == {
        'id': transaction.id,
        'asset': {
            'id': str(transaction.asset.id),
            'title': transaction.asset.title,
            'amount': transaction.asset.amount,
            'currency': {
                'id': transaction.asset.currency.id,
                'name': transaction.asset.currency.name,
                'code': transaction.asset.currency.code,
                'is_custom': transaction.asset.currency.is_custom,
                'rate_to_base_currency': float(
                    transaction.asset.currency.rate_to_base_currency)
            }
        },
        'category': {
            'id': transaction.category.id,
            'title': transaction.category.title,
            'type': transaction.category.type.value
        },
        'amount': float(transaction.amount),
        'created': transaction.created.isoformat()
    }


@pytest.mark.asyncio
async def test_add_transaction(
        asset: dto.Asset,
        transaction_category: dto.TransactionCategory,
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider
):
    token = auth.create_user_token(user)
    transaction_dict = {
        'asset_id': str(asset.id),
        'category_id': transaction_category.id,
        'amount': 10,
        'created': '2023-02-22 22:04'
    }
    resp = await client.post(
        '/api/v1/transaction/add',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
        json=transaction_dict
    )
    assert resp.is_success
    created_transaction = resp.json()

    resp = await client.get(
        f'/api/v1/transaction/{created_transaction["id"]}',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
    )

    assert resp.is_success
    assert created_transaction == resp.json()

    assert created_transaction == {
        'id': created_transaction['id'],
        'asset': {
            'id': str(asset.id),
            'title': asset.title,
            'amount': float(asset.amount) + transaction_dict['amount'],
            'currency': {
                'id': asset.currency.id,
                'name': asset.currency.name,
                'code': asset.currency.code,
                'is_custom': asset.currency.is_custom,
                'rate_to_base_currency': float(
                    asset.currency.rate_to_base_currency)
            }
        },
        'category': {
            'id': transaction_category.id,
            'title': transaction_category.title,
            'type': transaction_category.type.value
        },
        'amount': transaction_dict['amount'],
        'created': '2023-02-22T22:04:00'
    }


@pytest.mark.asyncio
async def test_delete_transaction(
        transaction: dto.Transaction,
        asset: dto.Asset,
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider,
        dao: DAO
):
    token = auth.create_user_token(user)
    resp = await client.delete(
        f'/api/v1/transaction/{transaction.id}',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
    )
    assert resp.is_success
    try:
        await dao.transaction.get_by_id(transaction.id)
    except TransactionNotFound:
        pass
    else:
        assert False

    asset_dto = await dao.asset.get_by_id(asset.id)

    assert asset.amount - transaction.amount == asset_dto.amount


@pytest.mark.asyncio
async def test_change_transaction(
        transaction: dto.Transaction,
        transaction_category: dto.TransactionCategory,
        asset: dto.Asset,
        currency: dto.Currency,
        client: AsyncClient,
        user: dto.User,
        auth: AuthProvider,
        dao: DAO
):
    token = auth.create_user_token(user)

    new_asset_dto = await dao.asset.create(dto.Asset(
        id=None,
        user_id=user.id,
        currency_id=currency.id,
        title='test change asset',
        amount=Decimal('15')
    ))
    await dao.commit()

    changed_transaction_dict = {
        'asset_id': str(new_asset_dto.id),
        'category_id': transaction_category.id,
        'amount': 5,
        'created': '2023-02-19 22:04',
        'id': transaction.id
    }
    resp = await client.put(
        '/api/v1/transaction/change',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
        json=changed_transaction_dict
    )

    assert resp.is_success

    asset_dto = await dao.asset.get_by_id(asset.id)
    assert asset.amount - transaction.amount == asset_dto.amount

    changed_asset_dto = await dao.asset.get_by_id(new_asset_dto.id)
    assert new_asset_dto.amount + changed_transaction_dict[
        'amount'] == changed_asset_dto.amount

    resp = await client.get(
        f'/api/v1/transaction/{changed_transaction_dict["id"]}',
        headers={
            'Authorization': 'Bearer ' + token.access_token},
    )
    assert resp.is_success
    changed_transaction_dict['created'] = '2023-02-19T22:04:00'
    assert resp.json() == {
        'id': changed_transaction_dict['id'],
        'asset': {
            'id': str(changed_asset_dto.id),
            'title': changed_asset_dto.title,
            'amount': float(changed_asset_dto.amount),
            'currency': {
                'id': currency.id,
                'name': currency.name,
                'code': currency.code,
                'is_custom': currency.is_custom,
                'rate_to_base_currency': float(
                    currency.rate_to_base_currency)
            }
        },
        'category': {
            'id': transaction_category.id,
            'title': transaction_category.title,
            'type': transaction_category.type.value
        },
        'amount': changed_transaction_dict['amount'],
        'created': '2023-02-19T22:04:00'
    }
