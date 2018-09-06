import unittest

from flask import current_app as app


class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_default_page(self):
        response = self.client.get('/parser/status')

        self.assertEquals(response.status_code, 200)
