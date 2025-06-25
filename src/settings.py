from __future__ import annotations

import os
from functools import cached_property
from pathlib import Path
from typing import Literal

import dotenv
import yaml
from pydantic import computed_field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

dotenv.load_dotenv(Path(__file__).parent / '..' / '.env')
if os.getenv('dev', 'False').lower() == 'true':
    secrets_dir = Path(__file__).parent / '..' / 'secrets'
else:
    secrets_dir = '/run/secrets'


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir=secrets_dir)

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir=secrets_dir)

    redis_host: str
    redis_port: int
    redis_user: str
    redis_password: str


class APISettings(BaseSettings):
    class Scope(BaseSettings):
        name: str
        description: str

    access_token_lifetime: int
    jwt_secret: str
    jwt_alg: str
    iss: str
    supported_pkce: list[Literal["S256", "plain"]]
    enabled_scopes: list[Scope]
    origins: list[HttpUrl]

    @computed_field
    @cached_property
    def compact_scopes(self) -> list[str]:
        return [scope.name for scope in self.enabled_scopes]

    @computed_field
    @cached_property
    def fastapi_scopes(self) -> dict[str, str]:
        return {scope.name: scope.description for scope in self.enabled_scopes}


def create_api_settings(settings_file_path: str | Path) -> "APISettings":
    with open(settings_file_path, encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return APISettings(**config)


_postgres_settings = PostgresSettings()
_redis_settings = RedisSettings()
_api_settings = create_api_settings(Path(__file__).parent / '..' / 'configs' / 'api.yaml')
