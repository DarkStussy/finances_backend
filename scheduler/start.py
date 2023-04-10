import asyncio

import aioschedule
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from finances.models.dto import Config
from scheduler.currency_prices import add_prices_task
from scheduler.fcsapi import FCSClient


async def scheduler(httpx_client: AsyncClient, ss: async_sessionmaker,
                    config: Config):
    fcs_client = FCSClient(access_key=config.fcsapi_access_key,
                           client=httpx_client)
    aioschedule.every().day.at('10:00').do(
        add_prices_task,
        fcs_client=fcs_client,
        ss=ss
    )

    await add_prices_task(fcs_client, ss)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(0.1)
