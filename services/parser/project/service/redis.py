from flask import Flask
from redis import Redis as Base


class Redis(Base):
    def __init__(self):
        pass

    def init_app(self, app: Flask):
        args = {
            'host': app.config.get('REDIS_HOST'),
            'port': app.config.get('REDIS_PORT'),
            'db': app.config.get('REDIS_DB')
        }

        super(Redis, self).__init__(**args)
