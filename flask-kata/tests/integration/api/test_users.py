import pytest
from pytest_mock import MockerFixture
from flask.testing import FlaskClient


class TestIndex:

    def test_list_users(self, client: FlaskClient):
        response = client.get('/api/users/')

        assert response.status_code == 200
        assert response.get_json() == []
