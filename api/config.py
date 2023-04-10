from datetime import timedelta

from dotenv import load_dotenv
from envparse import Env

from finances.models.dto import Config, DatabaseConfig, AuthConfig


def load_config() -> Config:
    load_dotenv()
    env = Env()

    return Config(
        db=DatabaseConfig(
            host=env.str('PG_HOST', default='0.0.0.0:5433'),
            username=env.str('PG_USERNAME', default='postgres'),
            password=env.str('PG_PASSWORD', default='postgres'),
            database=env.str('PG_DATABASE', default='postgres'),
        ),
        auth=AuthConfig(
            secret_key=env.str('SECRET_KEY'),
            token_expire=timedelta(days=365)
        ),
        fcsapi_access_key=env.str('FCSAPI_API_KEY')
    )
