import unittest

from project import redis
from flask import current_app as app


class ConfigTest(unittest.TestCase):
    def test_config(self):
        self.assertTrue(app.config.get('TESTING'))
        self.assertIsNotNone(app.config.get('SQLALCHEMY_DATABASE_URI'))
        self.assertIsNotNone(app.config.get('SECRET_KEY'))

    def test_redis(self):
        v1 = 10
        redis.set('test', v1)
        v2 = int(redis.get('test'))
        self.assertEquals(v1, v2)
