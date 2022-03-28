import pytest

from flask import Flask
from flask.testing import FlaskClient

from kata import create_app


@pytest.fixture
def app() -> Flask:
    app = create_app(test_config={
        'TESTING': True,
        'DATABASE_URL': 'sqlite://'
    })

    yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()
