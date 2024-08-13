import os
import tempfile

from flask.testing import FlaskClient
import pytest
from flask_server import create_app
from flask_server.db import init_db, dbAlchemy
from flask_server.config import Configuration
from sqlalchemy import text


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(test_config=Configuration(
        'dev', 
        f'sqlite:///{db_path}', 
        sql_logging=True, testing=True))

    with app.app_context():
        init_db()

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