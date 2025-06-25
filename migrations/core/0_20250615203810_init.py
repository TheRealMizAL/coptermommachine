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
    "software_version" VARCHAR(512),
    CONSTRAINT "uid_clientmeta_softwar_f0b867" UNIQUE ("software_id", "software_version")
);
CREATE TABLE IF NOT EXISTS "clientcontacts" (
    "contact" VARCHAR(256) NOT NULL,
    "client_id" UUID NOT NULL REFERENCES "clientmeta" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_clientconta_client__3683c0" ON "clientcontacts" ("client_id");
CREATE TABLE IF NOT EXISTS "clientcredentials" (
    "client_secret" VARCHAR(256) NOT NULL,
    "client_id_issued_at" INT NOT NULL,
    "client_secret_expires_at" INT NOT NULL DEFAULT 0,
    "client_id" UUID NOT NULL REFERENCES "clientmeta" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_clientcrede_client__a2179c" ON "clientcredentials" ("client_id");
CREATE TABLE IF NOT EXISTS "clientgranttypes" (
    "grant_type" VARCHAR(43) NOT NULL,
    "client_id" UUID NOT NULL REFERENCES "clientmeta" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_clientgrant_client__6aabb9" ON "clientgranttypes" ("client_id");
CREATE TABLE IF NOT EXISTS "clientjwks" (
    "jwk" VARCHAR(65536) NOT NULL,
    "client_id" UUID NOT NULL REFERENCES "clientmeta" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_clientjwks_client__d128d4" ON "clientjwks" ("client_id");
CREATE TABLE IF NOT EXISTS "clientresponsetypes" (
    "response_type" VARCHAR(43) NOT NULL,
    "client_id" UUID NOT NULL REFERENCES "clientmeta" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_clientrespo_client__ef9d4e" ON "clientresponsetypes" ("client_id");
CREATE TABLE IF NOT EXISTS "clientscopes" (
    "scope" VARCHAR(256) NOT NULL,
    "client_id" UUID NOT NULL REFERENCES "clientmeta" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_clientscope_client__034322" ON "clientscopes" ("client_id");
CREATE TABLE IF NOT EXISTS "redirecturis" (
    "uri" VARCHAR(2083) NOT NULL,
    "client_id" UUID NOT NULL REFERENCES "clientmeta" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_redirecturi_client__1e459a" ON "redirecturis" ("client_id");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
