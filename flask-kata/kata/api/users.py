from flask import (
    Blueprint,
    jsonify
)

from kata.entities import User

bp = Blueprint('users', __name__, url_prefix='/api/users')


@bp.route('/', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify(users)


