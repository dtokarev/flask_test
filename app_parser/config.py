import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://{}:{}@localhost/mv_download'.format('root', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_BINDS = {
        'db_resource': os.environ.get('RESOURCE_DATABASE_URL') or 'mysql://{}:{}@localhost/mv_resource'.format('root', 1),
    }
