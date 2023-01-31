import logging

import uvicorn

from fastapi import FastAPI, APIRouter
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from api import dependencies
from api.routes import setup_routers
from config import load_config


def main():
    logging.basicConfig(level=logging.DEBUG)

    # app = FastAPI(swagger_ui_parameters={"defaultModelsExpandDepth": -1})
    app = FastAPI()
    config = load_config()
    engine = create_async_engine(url=config.db.make_url, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    main_api_router = APIRouter()

    dependencies.setup(app, main_api_router, async_session, config)
    setup_routers(main_api_router)
    app.include_router(main_api_router, prefix='/api/v1')

    uvicorn.run(app, port=8000)


if __name__ == '__main__':
    main()
