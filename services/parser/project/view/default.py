from flask import Blueprint, jsonify

default_blueprint = Blueprint('default_routes', __name__, url_prefix='/parser')


@default_blueprint.route('/status', methods=['GET'])
def health():
    return jsonify({
        'status': 'success',
        'message': 'OK'
    })