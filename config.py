import os

basedir = os.path.abspath(os.path.dirname(__file__))


def get_secret(key):
    """
    gets application config params
    TODO: rewrite to db impl
    :param key:
    :return:
    """
    from params import configs

    return configs.get(key, None)


class Config:
    db_u = get_secret('DB_USERNAME')
    db_p = get_secret('DB_PASS')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://{}:{}@localhost/mv_media'.format(db_u, db_p)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
