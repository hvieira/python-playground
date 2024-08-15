
from flask import (
    Blueprint, jsonify, request
)


from flask_server.db import dbAlchemy

bp = Blueprint('auth_api', __name__, url_prefix='/auth')


@bp.get('/token')
def get_token():
    username = request.json['username']
    password = request.json['password']

    if not username or not password:
        return jsonify({'message': 'Required request parameters missing'}), 400

    dbAlchemy.session.get()