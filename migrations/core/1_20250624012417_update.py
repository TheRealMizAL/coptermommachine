from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "clientcredentials" ADD "client_key" VARCHAR(256) NOT NULL DEFAULT 'Nokey';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "clientcredentials" DROP COLUMN "client_key";"""
