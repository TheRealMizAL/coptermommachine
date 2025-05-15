from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "challanges" (
    "id" UUID NOT NULL PRIMARY KEY,
    "client_id" UUID NOT NULL,
    "code_challange" VARCHAR(128) NOT NULL,
    "code_challange_method" VARCHAR(5) NOT NULL
);
ALTER TABLE challanges OWNER TO oidc_schema_owner;
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
ALTER TABLE aerich OWNER TO oidc_schema_owner;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
