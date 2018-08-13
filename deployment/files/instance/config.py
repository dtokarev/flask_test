DEBUG = False
TESTING = False

SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}/lp_download'.format("{{db_user}}", "{{db_pass}}", "{{db_host}}")
SQLALCHEMY_BINDS = {
    'db_resource': 'mysql://{}:{}@{}/lp_resource'.format("{{db_user}}", "{{db_pass}}", "{{db_host}}")
}
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False
SQLALCHEMY_POOL_SIZE = 5
SQLALCHEMY_MAX_OVERFLOW = 100
SQLALCHEMY_POOL_RECYCLE = 60
