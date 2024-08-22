from flask import (
    Blueprint, current_app, g, jsonify, request
)
from sqlalchemy import select

from flask_server.api.auth import valid_token_required
from flask_server.db import dbAlchemy
from flask_server.models.post import Post
from flask_server.models.user import User, UserToken
from flask_server.api.requests import AuthTokenRequest
from flask_server.api.responses import UserTokenResponse
from flask_server.api.errors import OauthInvalidClient, OauthInvalidGrant, OauthInvalidRequest, OauthUnsupportedGrantType
from werkzeug.security import check_password_hash


bp = Blueprint('post_api', __name__)

@bp.get('/posts')
@valid_token_required
def get_posts():
    user = g.user

    posts = dbAlchemy.session.execute(select(Post).where(Post.author_id == user.id)).scalars().all()

    return jsonify(posts), 200    