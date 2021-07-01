from flask import (
    Blueprint,
    jsonify,
    request
)

from app.resources.auth import authenticated_client
from app.core import TODOTaskCore
from app.models import TODOTask


def create_blueprint(todo_tasks: TODOTaskCore):

    bp = Blueprint('todo_task', __name__, url_prefix='/api/v1/todo_tasks')

    @bp.route("/", methods=('GET',))
    def list_todo_tasks():
        results = todo_tasks.retrieve_todo_tasks()
        return jsonify([i.to_dict() for i in results])

    @bp.route("/", methods=('POST',))
    @authenticated_client
    def add_todo_task():
        task_json = request.get_json()
        task = TODOTask.from_dict(task_json)

        added_task = todo_tasks.add_task(task)

        return jsonify(added_task.to_dict())

    return bp
