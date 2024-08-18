
import datetime
import random
import string
from flask import (
    Blueprint, jsonify, request
)
from sqlalchemy import select

from flask_server.db import dbAlchemy
from flask_server.models.user import User, UserToken
from flask_server.api.requests import AuthTokenRequest
from flask_server.api.responses import UserTokenResponse
from flask_server.api.errors import InvalidRequest


bp = Blueprint('auth_api', __name__, url_prefix='/oauth')


@bp.post('/token')
def generate_token():
    try:
        token_request = AuthTokenRequest.from_json(request.json)
    except InvalidRequest as e:
        return jsonify(e.to_dict()), 400
    else:
        # TODO add a user "service" with these sort of functions for DRY purposes
        user = dbAlchemy.session.execute(select(User).where(User.username == token_request.username)).scalar()
        if user:
            token = UserToken(
                user_id = user.id,
                # TODO token length should be configurable - the longer the more "secure"
                token = ''.join(random.choices(string.ascii_letters, k=20)),
                # expiry should be configurable
                expiry = _get_new_token_expiry_datetime()
            )
            dbAlchemy.session.add(token)
            dbAlchemy.session.commit()

            return jsonify(UserTokenResponse.from_token(token).to_dict())

        else:
            # TODO implement
            pass

def _get_new_token_expiry_datetime() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)