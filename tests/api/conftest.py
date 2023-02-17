from _decimal import Decimal
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
from finances.database.models import Currency, Asset
from finances.exceptions.asset import AssetNotFound
from finances.exceptions.user import UserNotFound
from finances.models import dto
from finances.models.dto.config import Config
from tests.fixtures.asset_data import get_test_asset
from tests.fixtures.currency_data import get_test_currency
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
    return user_


@pytest_asyncio.fixture
async def currency(dao: DAO, user: dto.User) -> dto.Currency:
    curr_dto = get_test_currency()
    curr = await dao.currency.get_by_id(curr_dto.id)
    if curr:
        return curr

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
