from __future__ import annotations

from oidc_models import HttpsUrl


class OIDCError(Exception):
    def __init__(self, state: str, error_description: str | None = None, redirect_uri: HttpsUrl | None = None):
        self.redirect_uri: HttpsUrl | None = redirect_uri
        self.error: str = "server_error"
        self.error_description: str = error_description or (
            "The authorization server encountered an unexpected condition"
            " that prevented it from fulfilling the request."
        )
        self.state = state


class TemporarilyUnavalilable(OIDCError):

    def __init__(self, state: str, error_description: str | None = None, redirect_uri: HttpsUrl | None = None):
        self.error = "temporarily_unavailable"
        error_description = error_description or (
            "The authorization server is currently unable to handle the request "
            "due to a temporary overloading or maintenance of the server."
        )
        super().__init__(state, error_description, redirect_uri)
