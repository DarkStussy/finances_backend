import asyncio
from asyncio import AbstractEventLoop
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from alembic.command import upgrade
from alembic.config import Config as AlembicConfig
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, \
    async_sessionmaker
from sqlalchemy.orm import close_all_sessions

from finances.database.dao import DAO
from finances.models.dto.config import Config
from tests.load_test_config import load_test_config


@pytest.fixture(scope='session')
def path() -> Path:
    path = Path(__file__).parent
    return path


@pytest.fixture(scope='session')
def event_loop() -> AbstractEventLoop:
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


@pytest.fixture(scope='session')
def config() -> Config:
    return load_test_config()


@pytest.fixture(scope='session')
def postgres_url(config: Config) -> str:
    return config.db.make_url


@pytest.fixture(scope='session')
def alembic_config(postgres_url: str, path: Path) -> AlembicConfig:
    alembic_cfg = AlembicConfig(str(path.parent / 'alembic.ini'))
    alembic_cfg.set_main_option(
        'script_location',
        str(path.parent / 'finances' / 'database' / 'migrations')
    )

    alembic_cfg.set_main_option('sqlalchemy.url',
                                postgres_url.replace('asyncpg', 'psycopg2'))
    return alembic_cfg


@pytest.fixture(scope='session', autouse=True)
def upgrade_schema_db(alembic_config: AlembicConfig):
    upgrade(alembic_config, 'head')


@pytest_asyncio.fixture
async def dao(session: AsyncSession) -> DAO:
    dao_ = DAO(session=session)
    return dao_


async def clear_data(dao: DAO):
    await dao.user.delete_all()
    await dao.currency.delete_all()
    await dao.commit()


@pytest_asyncio.fixture
async def session(sessionmaker: async_sessionmaker) -> \
        AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as db_session:
        yield db_session


@pytest_asyncio.fixture(scope='session')
async def sessionmaker(postgres_url: str) \
        -> Generator[async_sessionmaker, None, None]:
    engine = create_async_engine(url=postgres_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    yield async_session
    await clear_data(DAO(async_session()))
    close_all_sessions()
