import pytest
from pytest_mock import MockerFixture
from flask.testing import FlaskClient


class TestIndex:

    def test_list_tasks(self, client: FlaskClient):
        response = client.get('/')

        assert response.status_code == 200
        assert response.get_data(as_text=True) == "Hello, World!"
