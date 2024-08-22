# TODO replace with "from typing import Self" with python 3.11
from __future__ import annotations
from dataclasses import dataclass, asdict
import datetime

from flask_server.json_encoding import ma
from flask_server.models.post import Post
from flask_server.models.user import User, UserToken
from marshmallow_sqlalchemy.fields import Nested


@dataclass
class UserTokenResponse():
    access_token: str
    expires_in: int
    token_type: str = 'Bearer'

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_token(token: UserToken) -> UserTokenResponse:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        diff = (token.expiry - now).seconds
        return UserTokenResponse(access_token=token.token, expires_in=diff)


class UserJson(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = ma.auto_field()
    username = ma.auto_field()


class PostResponse(ma.SQLAlchemySchema):
    class Meta:
        model = Post

    id = ma.auto_field()
    created = ma.auto_field()
    title = ma.auto_field()
    body = ma.auto_field()
    author = Nested(UserJson)

post_json = PostResponse()
post_json_list = PostResponse(many=True)