from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from settings import RedisSettings, _redis_settings


class RedisInitialisationError(Exception):
    pass


class RedisClient:
    def __init__(self, config: RedisSettings):
        self.client: Redis | None = None
        self.config = config

    async def connect(self):
        if not self.client:
            self.client = Redis(
                    host=self.config.redis_host,
                    port=self.config.redis_port,
                    username=self.config.redis_user,
                    password=self.config.redis_password,
                    db=0
            )
            await self.client.ping()
        else:
            raise RedisInitialisationError

    async def disconnect(self):
        if self.client:
            await self.client.close()


_redis = RedisClient(_redis_settings)


def register_redis(app: FastAPI, client: RedisClient):
    # noinspection PyProtectedMember
    from fastapi.routing import _merge_lifespan_context

    @asynccontextmanager
    async def redis_lifespan(app_instance: FastAPI):
        await client.connect()
        print('Redis initialized')
        yield
        await client.disconnect()
        print('Redis disconnected')

    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = _merge_lifespan_context(redis_lifespan, original_lifespan)
