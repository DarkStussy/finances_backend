from dataclasses import dataclass
from datetime import timedelta


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
        return f'{self.RDBMS}+{self.driver}://{self.username}:' \
               f'{self.password}@{self.host}/{self.database}'


@dataclass
class AuthConfig:
    secret_key: str
    token_expire: timedelta


@dataclass
class Config:
    db: DatabaseConfig
    auth: AuthConfig
    fcsapi_access_key: str
