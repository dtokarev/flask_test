from flask import Blueprint, jsonify
from flask import request

from project.domain.model import Search

parser_blueprint = Blueprint('parser_blueprint', __name__, url_prefix='/parser')


@parser_blueprint.route('/search', methods=['GET'])
def search_index():
    status = request.args.get('status', 'NEW').capitalize()
    searches = Search.query.filter_by(status=status).all()
    return jsonify([e.to_json() for e in searches])


@parser_blueprint.route('/search/<int:user_id>', methods=['GET'])
def search_view(user_id: int):
    search = Search.query.filter_by(id=user_id).first()
    return jsonify(search.to_json())


# @parser_blueprint.route('/queue', methods=['GET'])
# def queue_index():
#     from rq import Connection
#     from project import redis
#     from rq import Queue
#
#     with Connection(redis):
#         q = Queue()
#         jobs = q.get_jobs()
#
#     tasks = []
#     for job in jobs:
#         tasks.append({
#                 'task_id': job.get_id(),
#                 'task_status': job.get_status(),
#                 'task_result': job.result,
#                 'created_at': job.created_at,
#                 'description': job.description,
#             })
#
#     response = {
#         'status': 'success',
#         'tasks': tasks
#     }
#
#     return jsonify(response)
