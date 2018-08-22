import json

from nose import with_setup
from nose.tools import assert_equals
from app_parser import app

app_request = app.test_client()


def setup_func():
    app.testing = True


@with_setup(setup_func)
def test_health():
    res = app_request.get('/health')
    data = json.loads(res.data.decode("utf-8"))

    assert_equals(data.get("message"), "OK")
