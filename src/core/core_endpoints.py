from __future__ import annotations

import base64
from datetime import datetime, timedelta, UTC
from hashlib import sha256
from typing import Annotated, Literal

import jwt
from fastapi import APIRouter, Query, Form, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security.utils import get_authorization_scheme_param
from passlib.pwd import genword
from pydantic import UUID4, AnyHttpUrl
from tortoise.transactions import in_transaction
from utils.crypt import app_ctx

from oidc_models import AccessToken
from registration.db_models import ClientMeta, ClientCredentials
from settings import _api_settings
from utils.redis_client import _redis
from .core_exceptions import (UnauthorizedClientError, UnsupportedResponseTypeError, UnsupportedPKCEMethodError,
                              InvalidRequest, InvalidScopeError, InvalidGrantError, TokenInvalidRequestError,
                              UnauthrizedClientError)
from .core_models import RedisChallange, AppTokenResponse

core_router = APIRouter(tags=['core'])


async def verify_access_token(request: Request):
    authorization = request.headers.get("Authorization")
    scheme, param = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        raise HTTPException(
                status_code=401,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        token_raw = jwt.decode(param, _api_settings.jwt_secret, algorithms=[_api_settings.jwt_alg],
                               audience=[_api_settings.iss])
    except jwt.InvalidTokenError:
        raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
        )
    return AccessToken(**token_raw)


async def auth_helper(
        response_type: Literal["code"],
        client_id: UUID4,
        code_challange: str,
        state: str,
        app_token: str,
        code_challange_method: Literal["S256", "plain"] = "plain",
        redirect_uri: AnyHttpUrl | None = None,
        scope: str | None = None
):
    async with in_transaction():
        if not (client := await ClientMeta.get_or_none(id=client_id)):
            raise UnauthorizedClientError(
                    error_description=f"Client {client_id} does not exist",
                    state=state,
                    redirect_uri=redirect_uri
            )
        await client.fetch_related("redirect_uris", "response_types", "scopes")

        if response_type not in [r_type.response_type async for r_type in client.response_types.all()]:  # noqa
            raise UnsupportedResponseTypeError(
                    error_description=f"Client does not support \"{response_type}\" response type",
                    state=state,
                    redirect_uri=redirect_uri
            )
        if str(redirect_uri) not in [uri.uri async for uri in client.redirect_uris.all()]:  # noqa
            raise InvalidRequest(
                    error_description="Passed redirect URI is not registered for this client",
                    state=state,
                    redirect_uri=redirect_uri
            )
        allowed_scopes = [scope.scope async for scope in client.scopes.all()]  # noqa
        scope = scope or ''
        for req_scope in scope.split(' '):
            if req_scope not in _api_settings.compact_scopes:
                raise InvalidScopeError(
                        state=state,
                        redirect_uri=redirect_uri
                )
            elif req_scope not in allowed_scopes:
                raise InvalidScopeError(
                        error_description=f"Client does not support \"{req_scope}\" scope",
                        state=state,
                        redirect_uri=redirect_uri
                )
    if code_challange_method not in _api_settings.supported_pkce:
        raise UnsupportedPKCEMethodError(
                state=state,
                redirect_uri=redirect_uri
        )
    code = genword(entropy=56, length=32)
    await _redis.client.setex(f'session:{client_id}', 60,
                              RedisChallange(
                                      code=code,
                                      code_challange=code_challange,
                                      method=code_challange_method,
                                      req_scope=scope,
                                      redirect_uri=redirect_uri
                              ).model_dump_json())
    return RedirectResponse(
            status_code=302,
            url=f'{redirect_uri}?code={code}&state={state}'
    )


@core_router.get('/authorize')
async def get_auth_handeler(
        response_type: Annotated[Literal["code"], Query()],
        client_id: Annotated[UUID4, Query()],
        code_challange: Annotated[str, Query(min_length=43, max_length=48)],
        state: Annotated[str, Query()],
        app_token: Annotated[str, Query()],
        code_challange_method: Annotated[Literal["S256", "plain"], Query()] = "plain",
        redirect_uri: Annotated[AnyHttpUrl | None, Query()] = None,
        scope: Annotated[str | None, Query()] = None,
):
    return await auth_helper(
            response_type,
            client_id,
            code_challange,
            state,
            app_token,
            code_challange_method,
            redirect_uri,
            scope
    )


@core_router.post('/authorize')
async def post_auth_handler(
        response_type: Annotated[Literal["code"], Form()],
        client_id: Annotated[UUID4, Form()],
        code_challange: Annotated[str, Form(min_length=43, max_length=48)],
        state: Annotated[str, Form()],
        app_token: Annotated[str, Form()],
        code_challange_method: Annotated[Literal["S256", "plain"], Form()] = "plain",
        redirect_uri: Annotated[AnyHttpUrl | None, Form()] = None,
        scope: Annotated[str | None, Form()] = None,
):
    return await auth_helper(
            response_type,
            client_id,
            code_challange,
            state,
            app_token,
            code_challange_method,
            redirect_uri,
            scope
    )


@core_router.post('/token')
async def token_handler(
        grant_type: Annotated[Literal["authorization_code"], Form()],
        code: Annotated[str, Form()],
        code_vierfier: Annotated[str, Form()],
        redirect_uri: Annotated[AnyHttpUrl | None, Form()] = None,
        client_id: Annotated[UUID4, Form()] = None
) -> AppTokenResponse:
    if grant_type != "authorization_code":
        raise InvalidGrantError

    redis_record = await _redis.client.get(f'session:{client_id}')
    if not redis_record:
        raise TokenInvalidRequestError
    session_record: RedisChallange = RedisChallange.parse_raw(redis_record)

    if str(redirect_uri) != str(session_record.redirect_uri):
        raise TokenInvalidRequestError

    if code != session_record.code:
        raise TokenInvalidRequestError

    if session_record.method == 'S256':
        if session_record.code_challange != base64.b64encode(
                sha256(code_vierfier.encode('utf-8')).digest()).decode('utf-8'):
            raise TokenInvalidRequestError
    else:
        if session_record.code_challange != code_vierfier:
            raise TokenInvalidRequestError

    access_token = AccessToken(
            iss=_api_settings.iss,
            exp=int((datetime.now(UTC) + timedelta(seconds=_api_settings.access_token_lifetime)).timestamp()),
            iat=int(datetime.now(UTC).timestamp()),
            nbf=int(datetime.now(UTC).timestamp()),
            sub=client_id,
            aud=_api_settings.iss,
            client_id=client_id,
            scope=session_record.req_scope,
            nonce='random_string_i_swear'
    )
    encoded_access_token = jwt.encode(access_token.model_dump(exclude={'origins'}, mode='json'),
                                      _api_settings.jwt_secret,
                                      algorithm=_api_settings.jwt_alg)
    return AppTokenResponse(
            access_token=encoded_access_token,
            expires_in=_api_settings.access_token_lifetime
    )


@core_router.get('/get_key')
async def get_key(nonce: str,
                  acc_token: Annotated[AccessToken, Depends(verify_access_token)]):
    async with in_transaction():
        if not (client_creds := await ClientCredentials.get_or_none(client_id=acc_token.client_id)):
            raise UnauthrizedClientError()
    return {'key': client_creds.client_key}
