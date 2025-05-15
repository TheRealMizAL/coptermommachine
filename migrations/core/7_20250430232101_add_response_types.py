from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "clientresponsetypes" (
    "response_type" VARCHAR(43) NOT NULL UNIQUE,
    "client_id" UUID NOT NULL REFERENCES "clientmeta" ("id") ON DELETE CASCADE
);
ALTER TABLE clientresponsetypes OWNER TO oidc_schema_owner;
CREATE INDEX IF NOT EXISTS "idx_clientrespo_client__ef9d4e" ON "clientresponsetypes" ("client_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "clientresponsetypes";"""
