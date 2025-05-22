import os

from dynaconf import Dynaconf
from pydantic import BaseModel


class ScoreConfig(BaseModel):
    TRANSACTIONS_COUNT_WEIGHT: int
    TRANSACTIONS_FREQUENCY_WEIGHT: int
    TRANSACTIONS_QUALITY_WEIGHT: int
    TRANSACTIONS_TYPE_WEIGHT: int
    TRANSACTIONS_AMOUNT_WEIGHT: int
    TRANSACTIONS_FRAUD_WEIGHT: int


class AppConfig(BaseModel):
    debug: bool
    app_port: int
    app_version: str
    app_name: str
    app_host: str
    app_mount: str
    app_key: str
    secret_key: str
    cookie_name: str
    cookie_max_age_days: int


class DBConfig(BaseModel):
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int

    @property
    def url(self):
        path = 'postgresql+asyncpg://{0}:{1}@{2}:{3}/{4}'.format(
            self.db_user,
            self.db_password,
            os.getenv('POSTGRES_HOST') or self.db_host,
            self.db_port,
            self.db_name
        )
        return path


class Settings(BaseModel):
    app: AppConfig
    db: DBConfig
    score: ScoreConfig


dyna_settings = Dynaconf(
    settings_files=['settings.toml']
)


settings = Settings(
    app=dyna_settings['app_settings'],
    db=dyna_settings['db_settings'],
    score=dyna_settings['score_settings']
)