import asyncio
import logging

import httpx
import uvicorn

from fastapi import APIRouter
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from starlette.middleware.cors import CORSMiddleware

from api import v1
from api.config import load_config
from api.main_factory import create_app
from finances.models.dto import Config
from scheduler.start import scheduler


def start_scheduler(client: AsyncClient, ss: async_sessionmaker, config: Config):
    def func():
        asyncio.create_task(scheduler(client, ss, config))

    return func


def main():
    logging.basicConfig(level=logging.DEBUG)

    # app = FastAPI(swagger_ui_parameters={"defaultModelsExpandDepth": -1})
    app = create_app()
    config = load_config()
    engine = create_async_engine(url=config.db.make_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    client = httpx.AsyncClient()
    app.add_event_handler('startup', start_scheduler(client, async_session, config))
    app.add_event_handler('shutdown', client.aclose)
    api_router_v1 = APIRouter()

    v1.dependencies.setup(app, api_router_v1, async_session, config, client)
    v1.routes.setup_routers(api_router_v1)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "*",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    main_api_router = APIRouter(prefix='/api')
    main_api_router.include_router(api_router_v1, prefix='/v1')
    app.include_router(main_api_router)

    uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()
