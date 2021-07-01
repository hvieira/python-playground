import pytest

from flask.testing import FlaskClient

from app import create_app


@pytest.fixture
def app():
    app = create_app(test_config={
        'TESTING': True,
        'DATABASE_URL': 'sqlite://'
    })

    yield app


@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()
