import datetime

from fastapi import APIRouter, Response
from passlib.pwd import genword
from tortoise.exceptions import IntegrityError
from tortoise.transactions import atomic

from utils.crypt import app_ctx
from .db_models import (ClientMeta, ClientGrantTypes, ClientScopes, ClientContacts, ClientJWKs, ClientCredentials,
                        RedirectURIs, ClientResponseTypes)
from .reg_exceptions import InvalidClientMetadataError
from .reg_models import ClientRegistrationMeta

reg_router = APIRouter()


@reg_router.post(
        '/register',
        response_model_exclude_none=True,
        response_model_exclude_unset=True
)
@atomic()
async def register_client(response: Response, client_meta: ClientRegistrationMeta):
    try:
        client = ClientMeta(
                token_endpoint_auth_method=client_meta.token_endpoint_auth_method,
                client_name=client_meta.client_name,
                client_uri=client_meta.client_uri,
                logo_uri=client_meta.logo_uri,
                tos_uri=client_meta.tos_uri,
                policy_uri=client_meta.policy_uri,
                jwks_uri=client_meta.jwks_uri,
                software_id=client_meta.software_id,
                software_version=client_meta.software_version
        )
        await client.save()
    except IntegrityError:
        raise InvalidClientMetadataError(
                error_description="Client with given software_id and verison_id already exists",
                state=client_meta.state
        )
    await ClientGrantTypes.bulk_create(
            [ClientGrantTypes(client=client, grant_type=grant_type) for grant_type in client_meta.grant_types]
    )
    await ClientResponseTypes.bulk_create(
            [ClientResponseTypes(client=client, response_type=response_type) for response_type in
             client_meta.response_types]
    )
    await ClientScopes.bulk_create(
            [ClientScopes(client=client, scope=scope) for scope in client_meta.scope]
    )
    await ClientContacts.bulk_create(
            [ClientContacts(client=client, contact=contact) for contact in client_meta.contacts]
    )
    await ClientJWKs.bulk_create(
            [ClientJWKs(client=client, jwk=jwk.model_dump_json(exclude_none=True, exclude_unset=True)) for jwk in
             client_meta.jwks]
    )
    await RedirectURIs.bulk_create(
            [RedirectURIs(client=client, uri=uri) for uri in client_meta.redirect_uris]
    )
    client_secret = genword(entropy='secure', length=30)
    now_ts = datetime.datetime.now(datetime.UTC).timestamp()
    await ClientCredentials.create(
            client=client,
            client_secret=app_ctx.hash(client_secret),
            client_id_issued_at=now_ts,
            client_secret_expires_at=now_ts + 4_838_400  # valid for 28 days
    )

    full_client_data = await (await ClientMeta.get_or_none(id=client.id)).full()
    full_client_data['client_secret'] = client_secret
    full_client_data['state'] = client_meta.state
    response.status_code = 201
    return full_client_data
