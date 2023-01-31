import logging

import uvicorn

from fastapi import FastAPI, APIRouter
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from api import v1
from config import load_config


def main():
    logging.basicConfig(level=logging.DEBUG)

    # app = FastAPI(swagger_ui_parameters={"defaultModelsExpandDepth": -1})
    app = FastAPI()
    config = load_config()
    engine = create_async_engine(url=config.db.make_url, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    api_router_v1 = APIRouter()

    v1.dependencies.setup(app, api_router_v1, async_session, config)
    v1.routes.setup_routers(api_router_v1)

    main_api_router = APIRouter(prefix='/api')
    main_api_router.include_router(api_router_v1, prefix='/v1')

    app.include_router(main_api_router)

    uvicorn.run(app, port=8000)


if __name__ == '__main__':
    main()
