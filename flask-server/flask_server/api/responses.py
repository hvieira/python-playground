# TODO replace with "from typing import Self" with python 3.11
from __future__ import annotations
from dataclasses import dataclass, asdict
import datetime

from flask_server.models.user import UserToken


@dataclass
class UserTokenResponse():
    access_token: str
    expires_in: int
    token_type: str = 'Bearer'

    # TODO create a mixin for this
    def to_dict(self) -> dict:
        return asdict(self)
    
    @staticmethod
    def from_token(token: UserToken) -> UserTokenResponse:
        # TODO in reality the expiry should be "token expiry timestamp" - "token creation timestamp"
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        diff = (token.expiry - now).seconds
        return UserTokenResponse(access_token=token.token, expires_in=diff)
