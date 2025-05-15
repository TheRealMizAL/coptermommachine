from passlib.context import CryptContext

app_ctx = CryptContext(schemes=['pbkdf2_sha512', 'pbkdf2_sha256', 'bcrypt'])


def create_access_token():
    pass


def create_refresh_token():
    pass


def create_app_token(pre):
    pass
