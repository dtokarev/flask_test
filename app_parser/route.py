import time

from app_parser import app


@app.route('/<a>/<b>')
def test(a, b):
    time.sleep(1)
    return str(float(a)/float(b))

