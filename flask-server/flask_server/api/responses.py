# TODO replace with "from typing import Self" with python 3.11
from __future__ import annotations
from dataclasses import dataclass, asdict

from flask_server.models.user import UserToken


@dataclass
class UserTokenResponse():
    access_token: str

    # TODO create a mixin for this
    def to_dict(self) -> dict:
        return asdict(self)
    
    @staticmethod
    def from_token(token: UserToken) -> UserTokenResponse:
        return UserTokenResponse(access_token=token.token)