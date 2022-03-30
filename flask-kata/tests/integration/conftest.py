import pytest

from flask import Flask
from flask.testing import FlaskClient

from kata import create_app


@pytest.fixture
def app() -> Flask:
    app = create_app(test_config={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })

    yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()
