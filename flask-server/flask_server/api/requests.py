# TODO replace with "from typing import Self" with python 3.11
from __future__ import annotations
from dataclasses import dataclass

from flask_server.api.errors import OauthInvalidRequest


@dataclass(frozen=True)
class AuthTokenRequest():
    grant_type: str
    username: str
    password: str
    client_id: str
    client_secret: str

    @staticmethod
    def from_json(json: dict) -> AuthTokenRequest:
        try:
            return AuthTokenRequest(
                grant_type=json['grant_type'],
                username=json['username'],
                password=json['password'],
                client_id=json['client_id'],
                client_secret=json['client_secret'],
            )
        except KeyError:
            raise OauthInvalidRequest()
