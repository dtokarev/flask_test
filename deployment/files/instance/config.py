DEBUG = False
TESTING = False

SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@localhost/lp_download'.format({{db_user}}, {{db_pass}})
SQLALCHEMY_BINDS = {
    'db_resource': 'mysql://{}:{}@localhost/lp_resource'.format({{db_user}}, {{db_pass}})
}
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False
SQLALCHEMY_POOL_SIZE = 5
SQLALCHEMY_MAX_OVERFLOW = 100
SQLALCHEMY_POOL_RECYCLE = 60
