import os


class BaseConfig:
    TESTING = False
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY', '123seCret<>')

    JSON_AS_ASCII = False
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_MAX_OVERFLOW = 100
    SQLALCHEMY_POOL_RECYCLE = 60
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
    REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
    REDIS_DB = 0


class DevelopmentConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    DEBUG_TB_ENABLED = True

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True


class ProductionConfig(BaseConfig):
    pass

