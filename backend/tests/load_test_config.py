import os
from datetime import timedelta

from dotenv import load_dotenv

from finances.models.dto import Config, DatabaseConfig, AuthConfig


def load_test_config() -> Config:
    load_dotenv()

    return Config(
        db=DatabaseConfig(
            host=os.getenv('TEST_PG_HOST'),
            username=os.getenv('TEST_PG_USERNAME'),
            password=os.getenv('TEST_PG_PASSWORD'),
            database=os.getenv('TEST_PG_DATABASE'),
        ),
        auth=AuthConfig(
            secret_key=os.getenv('TEST_SECRET_KEY'),
            token_expire=timedelta(days=1)
        )
    )
