
from datetime import datetime, timezone
import functools
from flask import (
    Blueprint, abort, current_app, g, jsonify, request
)
from sqlalchemy import select

from flask_server.db import dbAlchemy
from flask_server.models.user import User, UserToken
from flask_server.api.requests import AuthTokenRequest
from flask_server.api.responses import UserTokenResponse
from flask_server.api.errors import OauthInvalidClient, OauthInvalidGrant, OauthInvalidRequest, OauthUnsupportedGrantType
from werkzeug.security import check_password_hash


bp = Blueprint('auth_api', __name__, url_prefix='/oauth')


@bp.post('/token')
def generate_token():
    token_request = AuthTokenRequest.from_json(request.json)

    validate_request(token_request)

    # TODO add a user "service" with these sort of functions for DRY purposes
    user = dbAlchemy.session.execute(select(User).where(User.username == token_request.username)).scalar()

    if user is None or not check_password_hash(user.password, token_request.password):
        raise OauthInvalidGrant()

    token = UserToken.create(user_id=user.id)
    dbAlchemy.session.add(token)
    dbAlchemy.session.commit()

    return jsonify(UserTokenResponse.from_token(token).to_dict())


def validate_request(token_request: AuthTokenRequest):
    if (
        token_request.client_id != current_app.config.get('OAUTH_CLIENT_ID') or 
        token_request.client_secret != current_app.config.get('OAUTH_CLIENT_SECRET')
    ):
        raise OauthInvalidClient()

    if token_request.grant_type != 'password':
        raise OauthUnsupportedGrantType()


def valid_token_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        authorizationHeader = request.headers.get('Authorization')
        if not authorizationHeader:
            abort(401, jsonify({'error': 'invalid credentials'}))
        
        bearer_token = authorizationHeader[7:]

        userToken = dbAlchemy.session.execute(select(UserToken)
                                              .where(UserToken.token == bearer_token)
                                              .where(UserToken.expiry > datetime.now(tz=timezone.utc))
                                              ).scalar()

        if not userToken:
            abort(401, jsonify({'error': 'invalid credentials'}))

        user = dbAlchemy.session.get(User, userToken.user_id)

        # should not happen, unless the user row was deleted
        if not user:
            abort(401, jsonify({'error': 'invalid credentials'}))

        g.user = user

        return view(**kwargs)

    return wrapped_view


@bp.errorhandler(OauthInvalidRequest)
def handle_invalid_request(_e):
    return jsonify({'error': 'invalid_request'}), 400

@bp.errorhandler(OauthInvalidClient)
def handle_invalid_request(_e):
    return jsonify({'error': 'invalid_client'}), 401

@bp.errorhandler(OauthUnsupportedGrantType)
def handle_invalid_request(_e):
    return jsonify({'error': 'unsupported_grant_type'}), 400

@bp.errorhandler(OauthInvalidGrant)
def handle_invalid_request(_e):
    return jsonify({'error': 'invalid_grant'}), 400
