from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "redirecturis" (
    "uri" VARCHAR(2083) NOT NULL,
    "client_id" UUID NOT NULL REFERENCES "clientmeta" ("id") ON DELETE CASCADE
);
ALTER TABLE redirecturis OWNER TO oidc_schema_owner;
CREATE INDEX IF NOT EXISTS "idx_redirecturi_client__1e459a" ON "redirecturis" ("client_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "redirecturis";"""
