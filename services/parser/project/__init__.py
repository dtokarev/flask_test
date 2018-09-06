import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

from project.service.alchemy import SQLAlchemy
from project.service.redis import Redis

db = SQLAlchemy()
redis = Redis()
migrate = Migrate()
ma = Marshmallow()
from .domain.model import *    # noqa


def config_logger(app: Flask):
    path = os.path.join(app.instance_path, 'log')
    if not os.path.isdir(path):
        os.mkdir(path)
    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler(os.path.join(app.instance_path, 'log', 'app.log'), maxBytes=10**8, backupCount=3)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.getenv('APP_SETTINGS'))

    from project.view import default_blueprint, parser_blueprint
    app.register_blueprint(default_blueprint)
    app.register_blueprint(parser_blueprint)

    config_logger(app)

    db.init_app(app)
    redis.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db, compare_type=app.config.get('DEBUG', False))

    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app


