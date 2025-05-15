from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "clientcredentials" (
    "client_secret" VARCHAR(128) NOT NULL,
    "client_id_issued_at" INT NOT NULL,
    "client_secret_expires_at" INT NOT NULL DEFAULT 0,
    "client_id" UUID NOT NULL REFERENCES "clientmeta" ("id") ON DELETE CASCADE
);
ALTER TABLE clientcredentials OWNER TO oidc_schema_owner;
CREATE INDEX IF NOT EXISTS "idx_clientcrede_client__a2179c" ON "clientcredentials" ("client_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "clientcredentials";"""
