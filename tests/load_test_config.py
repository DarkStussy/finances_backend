from datetime import timedelta
from envparse import Env

from finances.models.dto import Config, DatabaseConfig, AuthConfig


def load_test_config() -> Config:
    env = Env()
    env.read_envfile()

    return Config(
        db=DatabaseConfig(
            host=env.str('TEST_PG_HOST'),
            username=env.str('TEST_PG_USERNAME'),
            password=env.str('TEST_PG_PASSWORD'),
            database=env.str('TEST_PG_DATABASE'),
        ),
        auth=AuthConfig(
            secret_key=env.str('TEST_SECRET_KEY'),
            token_expire=timedelta(days=1)
        ),
        fcsapi_access_key=env.str('FCSAPI_API_KEY')
    )
