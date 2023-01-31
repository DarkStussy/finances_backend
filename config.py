import os
from dataclasses import dataclass
from datetime import timedelta

from dotenv import load_dotenv


@dataclass
class DatabaseConfig:
    host: str
    password: str
    username: str
    database: str
    RDBMS: str = 'postgresql'
    driver: str = 'asyncpg'

    @property
    def make_url(self):
        return f'{self.RDBMS}+{self.driver}://{self.username}:{self.password}@{self.host}/{self.database}'


@dataclass
class AuthConfig:
    secret_key: str
    token_expire: timedelta


@dataclass
class Config:
    db: DatabaseConfig
    auth: AuthConfig


def load_config() -> Config:
    load_dotenv()

    return Config(
        db=DatabaseConfig(
            host=os.getenv('PG_HOST'),
            username=os.getenv('PG_USERNAME'),
            password=os.getenv('PG_PASSWORD'),
            database=os.getenv('PG_DATABASE'),
        ),
        auth=AuthConfig(
            secret_key=os.getenv('SECRET_KEY'),
            token_expire=timedelta(days=1)
        )
    )
