from __future__ import annotations

from oidc_exceptions import OIDCError
from oidc_models import HttpsUrl


class RegistrationError(OIDCError):
    def __init__(self, state: str, error_description: str | None = None, redirect_uri: HttpsUrl | None = None):
        super().__init__(state, error_description, redirect_uri)


class InvalidRedirectUriError(RegistrationError):
    def __init__(self, state: str, error_description: str | None = None, redirect_uri: HttpsUrl | None = None):
        self.error = "invalid_redirect_uri"
        error_description = error_description or "The value of one or more redirection URIs is invalid"
        super().__init__(state, error_description, redirect_uri)


class InvalidClientMetadataError(RegistrationError):
    def __init__(self, state: str, error_description: str | None = None, redirect_uri: HttpsUrl | None = None):
        self.error = "invalid_client_metadata"
        error_description = error_description or (
            "The value of one of the client metadata fields is invalid and the"
            " server has rejected this request.  Note that an authorization server MAY choose to"
            " substitute a valid value for any requested parameter of a client's metadata"
        )
        super().__init__(state, error_description, redirect_uri)


class InvalidSoftwareStatementError(RegistrationError):
    def __init__(self, state: str, error_description: str | None = None, redirect_uri: HttpsUrl | None = None):
        self.error = "invalid_software_statement"
        error_description = error_description or "The software statement presented is invalid"
        super().__init__(state, error_description, redirect_uri)


class UnapprovedSoftwareStatementError(InvalidSoftwareStatementError):
    def __init__(self, state: str, error_description: str | None = None, redirect_uri: HttpsUrl | None = None):
        self.error = "unapproved_software_statement"
        error_description = error_description or (
            "The software statement presented is not approved for use by this authorization server"
        )
        super().__init__(state, error_description, redirect_uri)
