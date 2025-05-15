from __future__ import annotations

from oidc_exceptions import OIDCError
from oidc_models import HttpsUrl


class InvalidRequest(OIDCError):
    def __init__(self, state: str, error_description: str | None = None, redirect_uri: HttpsUrl | None = None):
        self.error = "invalid_request"
        error_description = error_description or (
            "The request is missing a required parameter,"
            " includes an invalid parameter value, includes a parameter more than once,"
            " or is otherwise malformed"
        )
        super().__init__(state, error_description, redirect_uri)


class CodeChallangeRequiredError(InvalidRequest):
    def __init__(self, state: str, error_description: str | None = None, redirect_uri: HttpsUrl | None = None):
        error_description = error_description or "Code challange required"
        super().__init__(state, error_description, redirect_uri)


class UnsupportedPKCEMethodError(InvalidRequest):
    def __init__(self, state: str, error_description: str | None = None, redirect_uri: HttpsUrl | None = None):
        error_description = error_description or "Unsupported PKCE method"
        super().__init__(state, error_description, redirect_uri)


class UnauthorizedClientError(OIDCError):
    def __init__(self, state: str, error_description: str | None = None, redirect_uri: HttpsUrl | None = None):
        self.error = "unauthorized_client"
        error_description = error_description or (
            "The client is not authorized to request an authorization code using this method"
        )
        super().__init__(state, error_description, redirect_uri)


class UnsupportedResponseTypeError(OIDCError):

    def __init__(self, state: str, error_description: str | None = None, redirect_uri: HttpsUrl | None = None):
        self.error = "unsupported_response_type"
        error_description = error_description or (
            "The authorization server does not support obtaining an authorization code using this method"
        )
        super().__init__(state, error_description, redirect_uri)


class InvalidScopeError(OIDCError):
    def __init__(self, state: str, error_description: str | None = None, redirect_uri: HttpsUrl | None = None):
        self.error = "invalid_scope"
        error_description = error_description or "The requested scope is invalid, unknown, or malformed"
        super().__init__(state, error_description, redirect_uri)


class TokenInvalidRequestError(OIDCError):

    def __init__(self, error_description: str | None = None):
        self.error = "invalid_request"
        error_description = error_description or ("The request is missing a required parameter,"
                                                  " includes an unsupported parameter value (other than grant type),"
                                                  " repeats a parameter, includes multiple credentials,"
                                                  " utilizes more than one mechanism for authenticating the client,"
                                                  " contains a code_verifier although no code_challenge was sent"
                                                  " in the authorization request, or is otherwise malformed")
        super().__init__('no_state_token', error_description)


class InvalidClient(TokenInvalidRequestError):
    def __init__(self, error_desciription: str | None = None):
        self.error = "invalid_client"
        error_desciription = error_desciription or "Client authentication failed"
        super().__init__(error_desciription)


class InvalidGrantError(TokenInvalidRequestError):
    def __init__(self, error_desciription: str | None = None):
        self.error = "invalid_grant"
        error_desciription = error_desciription or ("The provided authorization grant or refresh token is invalid, "
                                                    "expired, revoked, does not match the redirect URI used in the"
                                                    " authorization request, or was issued to another client.")
        super().__init__(error_desciription)


class UnauthrizedClientError(TokenInvalidRequestError):

    def __init__(self, error_desciription: str | None = None):
        self.error = "unauthorized_client"
        error_desciription = error_desciription or ("The authenticated client is not authorized to use"
                                                    " this authorization grant type.")
        super().__init__(error_desciription)


class UnsupportedGrantTypeError(TokenInvalidRequestError):

    def __init__(self, error_description: str | None = None):
        self.error = "unsupported_grant_type"
        error_description = error_description or ("The authorization grant type is not supported"
                                                  " by the authorization server.")
        super().__init__(error_description)


class TokenInvalidScopeError(TokenInvalidRequestError):

    def __init__(self, error_description: str | None = None):
        self.error = "invalid_scope"
        error_description = error_description or ("The requested scope is invalid, unknown, malformed, or exceeds"
                                                  " the scope granted by the resource owner.")
        super().__init__(error_description)
