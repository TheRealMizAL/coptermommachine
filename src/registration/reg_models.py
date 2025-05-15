from __future__ import annotations

from typing import Literal, Any

from pydantic import BaseModel, UUID4, model_validator, field_validator, Field, ConfigDict, ValidatorFunctionWrapHandler

from oidc_models import HttpsUrl
from settings import _api_settings
from .reg_exceptions import InvalidClientMetadataError

grant_response_lookup = {
    'authorization_code': 'code',
    'client_credentials': None,
    'refresh_token': None,
    'urn:ietf:params:oauth:grant-type:jwt-bearer': None
}


class JWKError(Exception):
    def __init__(self, description: str):
        self.description = description


class PubJWK(BaseModel):
    model_config = ConfigDict(frozen=True)

    kty: Literal["RSA", "EC"]
    use: Literal["sig", "enc"]
    key_ops: frozenset[Literal[
        "sign", "verify",
        "encrypt", "decrypt",
        "wrapKey", "unwrapKey",
        "deriveKey", "deriveBits"
    ]] | None = None
    alg: Literal[
             "RS256",
             "RS384",
             "RS512",
             "RSA-OAEP",
             "RSA-OAEP-256",
             "ES256",
             "ES384",
             "ES512",
         ] | None = None
    kid: UUID4 | None = None
    x5u: HttpsUrl | None = None
    x5c: frozenset[str] | None = None
    x5t: str | None = None
    x5t_s256: str | None = Field(default=None, alias="x5t#S256")

    # RSA
    n: str | None = None
    e: str | None = None

    # EC
    crv: Literal["P-256", "P-384", "P-521", "secp256k1"] | None = None
    x: str | None = None
    y: str | None = None

    @model_validator(mode='after')
    def validate_key_values(self):
        if any([self.n, self.e]) and any([self.crv, self.x, self.y]):
            raise JWKError("One of JWKs is invalid: cannot use values for RSA and EC simultaneously")
        if self.kty == "RSA" and not all([self.n, self.e]):
            raise JWKError("One of JWKs is invalid: n and e params must be passed with RSA algorithm")
        elif self.kty == "EC" and not all([self.crv, self.x, self.y]):
            raise JWKError("One of JWKs is invalid: crv, x and y params must be passed with EC algorithm")
        return self


# noinspection PyMethodParameters
class ClientRegistrationMeta(BaseModel):
    redirect_uris: list[HttpsUrl]
    token_endpoint_auth_method: Literal["none", "client_secret_post", "client_secret_basic"]
    grant_types: list[Literal[
        "authorization_code",
        "client_credentials",
        "refresh_token",
        "urn:ietf:params:oauth:grant-type:jwt-bearer"
    ]]
    response_types: list[Literal["code"]]
    state: str
    client_name: str | None = None
    client_uri: HttpsUrl | None = None
    logo_uri: HttpsUrl | None = None
    scope: str | None = None
    contacts: list[str] | None = None
    tos_uri: HttpsUrl | None = None
    policy_uri: HttpsUrl | None = None
    jwks_uri: HttpsUrl | None = None
    jwks: list[PubJWK] | None = None
    software_id: UUID4 | None = None
    software_version: str | None = None

    @field_validator('redirect_uris', 'grant_types', 'response_types', 'contacts', 'jwks', mode='after')
    def minimise_list(cls, value: list):
        return list(set(value))

    @field_validator('jwks', mode='wrap')
    def catch_jwks_errors(cls, value: list[PubJWK], handler: ValidatorFunctionWrapHandler):
        try:
            return handler(value)
        except JWKError as exc:
            raise InvalidClientMetadataError(
                    error_description=exc.description,
                    state=cls._raw_input['state']
            )

    @field_validator('scope')
    def minimise_scope(cls, value: str):
        validated_scopes = sorted(set(value.split(' ')))
        for scope in validated_scopes:
            if scope not in _api_settings.compact_scopes:
                raise InvalidClientMetadataError(
                        error_description=f"Scope \"{scope}\" is invalid, unknown, or malformed",
                        state=cls._raw_input['state']
                )
        return validated_scopes

    @model_validator(mode="before")
    def save_raw_input(cls, data: Any) -> Any:

        cls._raw_input = data
        return data

    @model_validator(mode='after')
    def check_grant_response_correlation(self):
        if self.jwks and self.jwks_uri:
            raise InvalidClientMetadataError(
                    error_description="Can't use both JWKs and JWKs URI",
                    state=self.state
            )

        for grant in self.grant_types:
            response_to_ensure = grant_response_lookup[grant]
            if response_to_ensure and response_to_ensure not in self.response_types:
                raise InvalidClientMetadataError(
                        error_description="Grant types do not match response types",
                        state=self.state
                )

        trusted_uris = [uri.host_with_scheme for uri in self.redirect_uris]
        if self.client_uri and self.client_uri.host_with_scheme not in trusted_uris:
            raise InvalidClientMetadataError(
                    error_description="Client URI's host with scheme not in redirect_uris",
                    state=self.state
            )
        if self.logo_uri and self.logo_uri.host_with_scheme not in trusted_uris:
            raise InvalidClientMetadataError(
                    error_description="Logo URI's host with scheme not in redirect_uris",
                    state=self.state
            )
        if self.tos_uri and self.tos_uri.host_with_scheme not in trusted_uris:
            raise InvalidClientMetadataError(
                    error_description="ToS URI's host with scheme not in redirect_uris",
                    state=self.state
            )
        if self.policy_uri and self.policy_uri.host_with_scheme not in trusted_uris:
            raise InvalidClientMetadataError(
                    error_description="Policy URI's host with scheme not in redirect_uris",
                    state=self.state
            )
        if self.jwks_uri and self.jwks_uri.host_with_scheme not in trusted_uris:
            raise InvalidClientMetadataError(
                    error_description="JWKs URI's host with scheme not in redirect_uris",
                    state=self.state
            )
        return self
