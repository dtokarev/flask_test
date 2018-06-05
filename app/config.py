import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://{}:{}@localhost/mv_media'.format('root', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
