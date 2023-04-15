import csv
from pathlib import Path

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import async_sessionmaker

from finances.database.models import Currency, CryptoCurrency


async def load_currencies(ss: async_sessionmaker):
    async with ss() as session:
        currencies_count = await session.execute(
            select(func.count()).select_from(Currency))
        module_path = Path(__file__).parent
        if not currencies_count.scalar():
            currencies_path = module_path / 'currencies.csv'
            with open(currencies_path, mode='r') as f:
                reader = csv.reader(f, delimiter=',')
                for row in reader:
                    session.add(
                        Currency(
                            id=int(row[0]),
                            name=row[1],
                            code=row[2],
                            is_custom=False
                        )
                    )

            await session.commit()
        crypto_currencies_count = await session.execute(
            select(func.count()).select_from(CryptoCurrency)
        )
        if not crypto_currencies_count.scalar():
            crypto_currencies_path = module_path / 'cryptocurrencies.csv'
            with open(crypto_currencies_path, mode='r') as f:
                reader = csv.reader(f, delimiter=',')
                for row in reader:
                    session.add(
                        CryptoCurrency(
                            id=int(row[0]),
                            name=row[1],
                            code=row[2]
                        )
                    )

            await session.commit()
