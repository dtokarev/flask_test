from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app_parser.logger import config_logger


class CustomAlchemy(SQLAlchemy):
    def apply_driver_hacks(self, app, info, options):
        if "isolation_level" not in options:
            options["isolation_level"] = "READ COMMITTED"

        return super(CustomAlchemy, self).apply_driver_hacks(app, info, options)


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    return app

app = create_app()
config_logger(app)
db = CustomAlchemy(app)
migrate = Migrate(app, db, compare_type=app.config.get('DEBUG', False))

from app_parser import route
from app_parser.domain import model
