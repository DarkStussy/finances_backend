from _decimal import Decimal
from datetime import datetime
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI, APIRouter
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from api import v1
from api.main_factory import create_app
from api.v1.dependencies import AuthProvider
from finances.database.dao import DAO
from finances.database.models import Currency, Asset, TransactionCategory
from finances.exceptions.asset import AssetNotFound
from finances.exceptions.crypto_asset import CryptoAssetNotFound
from finances.exceptions.crypto_currency import CryptoCurrencyNotFound
from finances.exceptions.crypto_portfolio import CryptoPortfolioNotFound
from finances.exceptions.crypto_transaction import CryptoTransactionNotFound
from finances.exceptions.currency import CurrencyNotFound
from finances.exceptions.transaction import TransactionCategoryNotFound, \
    TransactionNotFound
from finances.exceptions.user import UserNotFound
from finances.models import dto
from finances.models.dto.config import Config
from tests.fixtures.asset_data import get_test_asset
from tests.fixtures.crypto_currency_data import get_test_cryptocurrency, \
    get_test_cryptocurrency2
from tests.fixtures.crypto_portfolio_data import get_test_crypto_portfolio
from tests.fixtures.crypto_transaction_data import get_test_crypto_transaction
from tests.fixtures.currency_data import get_test_currency
from tests.fixtures.transaction_data import get_test_transaction_category
from tests.fixtures.user_data import get_test_user


@pytest.fixture(scope='session')
def app(config: Config, sessionmaker: async_sessionmaker) -> FastAPI:
    app = create_app()
    api_router_v1 = APIRouter()
    v1.dependencies.setup(app, api_router_v1, sessionmaker, config)
    v1.routes.setup_routers(api_router_v1)
    main_api_router = APIRouter(prefix='/api')
    main_api_router.include_router(api_router_v1, prefix='/v1')

    app.include_router(main_api_router)
    return app


@pytest_asyncio.fixture(scope='session')
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app,
                           base_url='http://127.0.0.1:8000') as async_client:
        yield async_client


@pytest.fixture(scope='session')
def auth(config: Config) -> AuthProvider:
    return AuthProvider(config.auth)


@pytest_asyncio.fixture
async def user(dao: DAO, auth: AuthProvider) -> dto.User:
    test_user = get_test_user()
    try:
        user_ = await dao.user.get_by_username(test_user.username)
    except UserNotFound:
        password = auth.get_password_hash('12345')
        user_ = await dao.user.create(test_user.add_password(password))
        await dao.commit()
    return user_


@pytest_asyncio.fixture
async def currency(dao: DAO, user: dto.User) -> dto.Currency:
    curr_dto = get_test_currency()
    try:
        curr = await dao.currency.get_by_id(curr_dto.id)
    except CurrencyNotFound:
        curr = await dao.session.merge(
            Currency(
                id=curr_dto.id,
                name=curr_dto.name,
                code=curr_dto.code,
                is_custom=True,
                rate_to_base_currency=Decimal('0.1'),
                user_id=user.id,
            )
        )
        await dao.commit()
        return curr.to_dto()
    else:
        return curr


@pytest_asyncio.fixture
async def asset(dao: DAO, user: dto.User, currency: dto.Currency) -> dto.Asset:
    asset_dto = get_test_asset()
    try:
        asset_ = await dao.asset.get_by_id(asset_dto.id)
    except AssetNotFound:
        asset_dto.user_id = user.id
        asset_dto.currency_id = currency.id
        asset_ = Asset.from_dto(asset_dto)
        asset_.id = asset_dto.id
        await dao.session.merge(asset_)
        await dao.commit()
        asset_ = asset_.to_dto(with_currency=False)
        asset_.currency = currency
    return asset_


@pytest_asyncio.fixture
async def transaction_category(dao: DAO,
                               user: dto.User) -> dto.TransactionCategory:
    category_dto = get_test_transaction_category()
    try:
        category = await dao.transaction_category.get_by_id(category_dto.id)
    except TransactionCategoryNotFound:
        category_dto.user_id = user.id
        category = TransactionCategory.from_dto(category_dto)
        category = await dao.session.merge(category)
        category = category.to_dto()
        await dao.commit()

    return category


@pytest_asyncio.fixture
async def transaction(
        dao: DAO,
        user: dto.User,
        asset: dto.Asset,
        transaction_category: dto.TransactionCategory
) -> dto.Transaction:
    try:
        transaction_dto = await dao.transaction.get_by_id(1)
    except TransactionNotFound:
        transaction_dto = dto.Transaction(
            id=1,
            user_id=user.id,
            asset_id=asset.id,
            category_id=transaction_category.id,
            amount=Decimal('5.0'),
            created=datetime.now()
        )
        transaction_dto = await dao.transaction.merge(transaction_dto)
        await dao.commit()
        transaction_dto.asset = asset
        transaction_dto.category = transaction_category

    return transaction_dto


@pytest_asyncio.fixture
async def crypto_portfolio(
        dao: DAO,
        user: dto.User,
) -> dto.CryptoPortfolio:
    crypto_portfolio_dto = get_test_crypto_portfolio()
    try:
        crypto_portfolio_dto = await dao.crypto_portfolio.get_by_id(
            crypto_portfolio_dto.id)
    except CryptoPortfolioNotFound:
        crypto_portfolio_dto.user_id = user.id
        crypto_portfolio_dto = await dao.crypto_portfolio.merge(
            crypto_portfolio_dto)
        await dao.user.set_base_crypto_portfolio(user, crypto_portfolio_dto.id)
        await dao.commit()

    return crypto_portfolio_dto


@pytest_asyncio.fixture
async def crypto_currency(
        dao: DAO
) -> dto.CryptoCurrency:
    crypto_currency_dto = get_test_cryptocurrency()
    try:
        crypto_currency_dto = await dao.crypto_currency.get_by_id(
            crypto_currency_dto.id)
    except CryptoCurrencyNotFound:
        crypto_currency_dto = await dao.crypto_currency.merge(
            crypto_currency_dto)
        await dao.commit()

    return crypto_currency_dto


@pytest_asyncio.fixture
async def crypto_currency2(
        dao: DAO
) -> dto.CryptoCurrency:
    crypto_currency_dto = get_test_cryptocurrency2()
    try:
        crypto_currency_dto = await dao.crypto_currency.get_by_id(
            crypto_currency_dto.id)
    except CryptoCurrencyNotFound:
        crypto_currency_dto = await dao.crypto_currency.merge(
            crypto_currency_dto)
        await dao.commit()

    return crypto_currency_dto


@pytest_asyncio.fixture
async def crypto_asset(
        user: dto.User,
        crypto_portfolio: dto.CryptoPortfolio,
        crypto_currency: dto.CryptoCurrency,
        dao: DAO
) -> dto.CryptoAsset:
    try:
        crypto_asset_dto = await dao.crypto_asset.get_by_id(1)
    except CryptoAssetNotFound:
        crypto_asset_dto = await dao.crypto_asset.merge(
            dto.CryptoAsset(
                id=1,
                user_id=user.id,
                portfolio_id=crypto_portfolio.id,
                crypto_currency_id=crypto_currency.id,
                amount=None
            )
        )
        await dao.commit()
        crypto_asset_dto.crypto_currency = crypto_currency
    return crypto_asset_dto


@pytest_asyncio.fixture
async def crypto_transaction(
        user: dto.User,
        crypto_portfolio: dto.CryptoPortfolio,
        crypto_asset: dto.CryptoAsset,
        dao: DAO
) -> dto.CryptoTransaction:
    crypto_transaction_dto = get_test_crypto_transaction()
    try:
        crypto_transaction_dto = await dao.crypto_transaction.get_by_id(
            crypto_transaction_dto.id
        )
    except CryptoTransactionNotFound:
        crypto_transaction_dto.user_id = user.id
        crypto_transaction_dto.portfolio_id = crypto_portfolio.id
        crypto_transaction_dto.crypto_asset_id = crypto_asset.id
        crypto_transaction_dto = await dao.crypto_transaction.merge(
            crypto_transaction_dto)
        await dao.commit()

    return crypto_transaction_dto
