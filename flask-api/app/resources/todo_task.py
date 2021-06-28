from flask import (
    Blueprint,
    jsonify
)

from app.core import TODOTaskCore


def create_blueprint(todo_tasks: TODOTaskCore):

    bp = Blueprint('todo_task', __name__, url_prefix='/api/v1/todo_tasks')

    @bp.route("/", methods=('GET',))
    def list_todo_tasks():
        results = todo_tasks.retrieve_todo_tasks()
        return jsonify([i.to_dict() for i in results])

    return bp
