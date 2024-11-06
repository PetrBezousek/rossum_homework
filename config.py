class Config:
    """Base config, uses staging database server."""
    DEBUG = False
    USERNAME = ''

class ProductionConfig(Config):
    """Uses production database server."""
    DB_SERVER = '192.168.19.32'

class DevelopmentConfig(Config):
    DB_SERVER = 'localhost'

class TestingConfig(Config):
    DB_SERVER = 'localhost'