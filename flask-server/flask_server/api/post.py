from flask import (
    Blueprint, Request, g, request
)
from sqlalchemy import select

from flask_server.api.auth import valid_token_required
from flask_server.db import dbAlchemy
from flask_server.models.post import Post, post_json_list


bp = Blueprint('post_api', __name__)

@bp.get('/posts')
@valid_token_required
def get_posts():
    user = g.user

    pagination_spec = pagination_from_request(request)

    posts = dbAlchemy.session.execute(
        select(Post)
        .where(Post.author_id == user.id)
        .where(Post.id > pagination_spec[1])
        .order_by(Post.id.asc())
        .limit(pagination_spec[0])
    ).scalars().all()

    return post_json_list.dump(posts)


def pagination_from_request(request: Request) -> tuple[int, int]:
    return (
        request.args.get("page_size", default=20),
        request.args.get("offset_cursor", default=0),
    )
