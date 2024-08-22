from datetime import datetime, timedelta, timezone
import os
from flask import Flask
import pytest
import tempfile

from flask.testing import FlaskClient
from sqlalchemy import select

from flask_server import create_app
from flask_server.config import Configuration
from flask_server.models.post import Post
from flask_server.models.user import User, UserToken


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    # TODO run tests inside docker network
    app = create_app(test_config=Configuration(
        secret_key='dev', 
        db_uri=f'postgresql://root:root@localhost:5433/test',
        oauth_client_id='test_oauth_client_it',
        oauth_client_secret='test_oauth_client_secretz',
        testing=True
        )
    )

    init_db(app)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def register(self, username='test', password='test'):
        return self._client.post(
            '/auth/register',
            data={'username': username, 'password': password}
        )
    

    def get_user_from_username(self, app: Flask, username='test'):
        with app.app_context():
            from flask_server.db import dbAlchemy

            return dbAlchemy.session.execute(select(User).where(User.username == username)).scalar_one()

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')
    
    def create_api_token(self, app: Flask, for_user_with_username='test', created: datetime=None, expiry: datetime=None) -> str:
        # with app.app_context():
        user = self.get_user_from_username(app, for_user_with_username)
        token = UserToken(
            user_id=user.id,
            token='dummyTokenBlahBlah_!',
            created=datetime.now(tz=timezone.utc) if created is None else created,
            expiry=datetime.now(tz=timezone.utc) + timedelta(hours=1) if expiry is None else expiry
        )

        from flask_server.db import dbAlchemy
        
        # TODO need proper handling of all of this - there's other places as well
        dbAlchemy.session.add(token)
        dbAlchemy.session.commit()
        dbAlchemy.session.flush()

        return token.token


@pytest.fixture
def auth(client):
    return AuthActions(client)


class PostActions():

    def create_post(self, p: Post) -> None:
        # with self._app.app_context():
        from flask_server.db import dbAlchemy
        dbAlchemy.session.add(p)
        dbAlchemy.session.commit()
        dbAlchemy.session.flush()

@pytest.fixture
def posting():
    return PostActions()


def init_db(app: Flask):
    from flask_server.db import dbAlchemy
    with app.app_context():
        dbAlchemy.drop_all()
        dbAlchemy.create_all()


def serialize_dt_iso_format(dt: datetime) -> str:
    return dt.isoformat()
