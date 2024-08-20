import os
from flask import Flask
import pytest
import tempfile

from flask.testing import FlaskClient

from flask_server import create_app
from flask_server.config import Configuration


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    # TODO run tests inside docker network
    app = create_app(test_config=Configuration(
        secret_key='dev', 
        db_uri=f'postgresql://root:root@localhost:5433/test',
        oauth_client_id='test_oauth_client_it',
        oauth_client_secret='test_oauth_client_secretz',
        sql_logging=True, 
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

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)


def init_db(app: Flask):
    from flask_server.db import dbAlchemy
    with app.app_context():
        dbAlchemy.drop_all()
        dbAlchemy.create_all()
