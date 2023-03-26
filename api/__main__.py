import logging

import httpx
import uvicorn

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from starlette.middleware.cors import CORSMiddleware

from api import v1
from api.config import load_config
from api.main_factory import create_app


def main():
    logging.basicConfig(level=logging.DEBUG)

    # app = FastAPI(swagger_ui_parameters={"defaultModelsExpandDepth": -1})
    app = create_app()
    config = load_config()
    engine = create_async_engine(url=config.db.make_url, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    client = httpx.AsyncClient()
    app.add_event_handler('shutdown', client.aclose)

    api_router_v1 = APIRouter()

    v1.dependencies.setup(app, api_router_v1, async_session, config, client)
    v1.routes.setup_routers(api_router_v1)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    main_api_router = APIRouter(prefix='/api')
    main_api_router.include_router(api_router_v1, prefix='/v1')
    app.include_router(main_api_router)
    return app


if __name__ == '__main__':
    uvicorn.run('api:main', factory=True, log_config=None)
