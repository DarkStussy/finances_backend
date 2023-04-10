import csv
import logging

from sqlalchemy.ext.asyncio import async_sessionmaker

from finances.database.dao.currency_price import CurrencyPriceDAO
from finances.database.models import Currency
from scheduler.fcsapi import FCSClient


async def add_prices_task(fcs_client: FCSClient, ss: async_sessionmaker):
    currency_prices = await fcs_client.get_all_prices()
    async with ss() as session:
        currency_price_dao = CurrencyPriceDAO(session=session)
        await currency_price_dao.add_many(currency_prices)
        await currency_price_dao.commit()

        with open('../currencies.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                currency = Currency(name=row[1], code=row[2], is_custom=False)
                session.add(currency)
            await session.commit()

    logging.info('CURRENCY PRICES SUCCESSFULLY UPDATED')
