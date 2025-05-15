from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "clientcredentials" ALTER COLUMN "client_secret" TYPE VARCHAR(256) USING "client_secret"::VARCHAR(256);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "clientcredentials" ALTER COLUMN "client_secret" TYPE VARCHAR(128) USING "client_secret"::VARCHAR(128);"""
