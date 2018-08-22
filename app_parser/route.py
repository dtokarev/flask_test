from flask import jsonify

from app_parser import app


@app.route('/health')
def health():
    return jsonify({'message': 'OK'})


# @app.handle_exception('404')
# def handle_404():
#     return '404 Not found', 404
