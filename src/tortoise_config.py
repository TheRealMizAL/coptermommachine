from settings import _postgres_settings

CONFIG = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': _postgres_settings.postgres_host,
                'port': _postgres_settings.postgres_port,
                'user': _postgres_settings.postgres_user,
                'password': _postgres_settings.postgres_password,
                'database': _postgres_settings.postgres_db
            }
        }
    },
    'apps': {
        'core': {
            'models': ['core.db_models', 'registration.db_models', 'aerich.models'],
            'default_connection': 'default'
        }
    }
}
