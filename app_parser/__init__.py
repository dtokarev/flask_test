from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    return app

app = create_app()
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app_parser import route
from app_parser.domain import model
