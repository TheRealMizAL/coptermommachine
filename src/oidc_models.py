from pydantic import AnyUrl, UrlConstraints, BaseModel, UUID4


class AnyHttpsUrl(AnyUrl):
    """A type that will accept any https URL.

    * TLD required
    * Host not required
    """

    _constraints = UrlConstraints(allowed_schemes=['https'])


class HttpsUrl(AnyUrl):

    _constraints = UrlConstraints(max_length=2083, allowed_schemes=['https'])

    @property
    def host_with_scheme(self):
        return f'{self.scheme}://{self.host}'


class AppToken(BaseModel):
    iss: HttpsUrl
    sub: UUID4
    aud: UUID4
    exp: int
    iat: int
    auth_time: int
    nonce: str
    at_hash: str
