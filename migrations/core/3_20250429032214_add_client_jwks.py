from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
CREATE TABLE IF NOT EXISTS "clientjwks" (
    "jwk" VARCHAR(65536) NOT NULL,
    "client_id" UUID NOT NULL REFERENCES "clientmeta" ("id") ON DELETE CASCADE
);
ALTER TABLE clientjwks OWNER TO oidc_schema_owner;
CREATE INDEX IF NOT EXISTS "idx_clientjwks_client__d128d4" ON "clientjwks" ("client_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uid_clientconta_contact_d08c6f" ON "clientcontacts" ("contact");
CREATE UNIQUE INDEX IF NOT EXISTS "uid_clientgrant_grant_t_9bf818" ON "clientgranttypes" ("grant_type");
CREATE UNIQUE INDEX IF NOT EXISTS "uid_clientscope_scope_0658af" ON "clientscopes" ("scope");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "uid_clientgrant_grant_t_9bf818";
        DROP INDEX IF EXISTS "uid_clientconta_contact_d08c6f";
        DROP INDEX IF EXISTS "uid_clientscope_scope_0658af";
        DROP TABLE IF EXISTS "clientjwks";"""
