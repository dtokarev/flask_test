import time

from flask import jsonify

from app_parser import app

a = ['test']


@app.route('/')
def test():
    a.append('fsfs')
    return jsonify(a)

