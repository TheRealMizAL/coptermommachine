from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
CREATE TABLE IF NOT EXISTS "clientmeta" (
    "id" UUID NOT NULL PRIMARY KEY,
    "token_endpoint_auth_method" VARCHAR(19) NOT NULL,
    "client_name" VARCHAR(1024),
    "client_uri" VARCHAR(2083),
    "logo_uri" VARCHAR(2083),
    "tos_uri" VARCHAR(2083),
    "policy_uri" VARCHAR(2083),
    "jwks_uri" VARCHAR(2083),
    "software_id" UUID,
    "software_version" VARCHAR(512)
);
ALTER TABLE clientmeta OWNER TO oidc_schema_owner;
CREATE TABLE IF NOT EXISTS "clientcontacts" (
    "contact" VARCHAR(256) NOT NULL,
    "client_id" UUID NOT NULL REFERENCES "clientmeta" ("id") ON DELETE CASCADE
);
ALTER TABLE clientcontacts OWNER TO oidc_schema_owner;
CREATE TABLE IF NOT EXISTS "clientgranttypes" (
    "grant_type" VARCHAR(43) NOT NULL,
    "client_id" UUID NOT NULL REFERENCES "clientmeta" ("id") ON DELETE CASCADE
);
ALTER TABLE clientgranttypes OWNER TO oidc_schema_owner;
CREATE TABLE IF NOT EXISTS "clientscopes" (
    "scope" VARCHAR(256) NOT NULL,
    "client_id" UUID NOT NULL REFERENCES "clientmeta" ("id") ON DELETE CASCADE
);
ALTER TABLE clientscopes OWNER TO oidc_schema_owner;

CREATE INDEX IF NOT EXISTS "idx_clientconta_client__3683c0" ON "clientcontacts" ("client_id");
CREATE INDEX IF NOT EXISTS "idx_clientgrant_client__6aabb9" ON "clientgranttypes" ("client_id");
CREATE INDEX IF NOT EXISTS "idx_clientscope_client__034322" ON "clientscopes" ("client_id");
DROP TABLE IF EXISTS "challanges";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "clientmeta";
        DROP TABLE IF EXISTS "clientscopes";
        DROP TABLE IF EXISTS "clientcontacts";
        DROP TABLE IF EXISTS "clientgranttypes";"""
