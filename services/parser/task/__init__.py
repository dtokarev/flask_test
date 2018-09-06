from flask.cli import FlaskGroup

from project import create_app

cli = FlaskGroup(create_app=create_app, load_dotenv=False)

from . import test, populate, parse
