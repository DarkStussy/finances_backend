from fastapi import FastAPI, APIRouter
from sqlalchemy.ext.asyncio import async_sessionmaker

from api.v1.dependencies.auth import AuthProvider, get_current_user, \
    get_auth_provider
from api.v1.dependencies.db import DatabaseProvider, dao_provider
from finances.models.dto.config import Config


def setup(app: FastAPI,
          api_router: APIRouter,
          db_sessionmaker: async_sessionmaker,
          config: Config):
    db_provider = DatabaseProvider(session=db_sessionmaker)
    auth_provider = AuthProvider(config.auth)

    api_router.include_router(auth_provider.router)

    app.dependency_overrides[dao_provider] = db_provider.dao
    app.dependency_overrides[get_current_user] = auth_provider.get_current_user
    app.dependency_overrides[get_auth_provider] = lambda: auth_provider
