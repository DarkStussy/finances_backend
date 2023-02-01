from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI, APIRouter
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from api import v1
from api.main_factory import create_app
from api.v1.dependencies import AuthProvider
from finances.models.dto.config import Config


@pytest.fixture(scope="session")
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
