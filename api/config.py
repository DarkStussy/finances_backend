import os
from datetime import timedelta

from dotenv import load_dotenv

from finances.models.dto import Config, DatabaseConfig, AuthConfig


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
            token_expire=timedelta(days=365)
        ),
        fcsapi_access_key=os.getenv('FCSAPI_API_KEY')
    )
