import uuid

import pytest
from pytest_mock import MockerFixture
from flask.testing import FlaskClient

from app.db import db_session
from app.models import TODOTask


@pytest.fixture
def some_todo_tasks():
    tasks = [
        TODOTask(str(uuid.uuid4()), 'Task 1'),
        TODOTask(str(uuid.uuid4()), 'Task 2'),
        TODOTask(str(uuid.uuid4()), 'Task 3'),
    ]

    for t in tasks:
        db_session.add(t)
        db_session.commit()

    return tasks


@pytest.fixture
def valid_auth_token():
    return 'dummy-token'


class TestTODOTaskResource:

    def test_list_tasks(self, client: FlaskClient, some_todo_tasks):
        response = self.get_tasks(client)

        assert response.status_code == 200
        assert response.get_json() == [i.to_dict() for i in some_todo_tasks]

    def test_add_task(self, client: FlaskClient, valid_auth_token):
        todo_task_content = 'lorem ipsum'

        add_response = client.post(
            '/api/v1/todo_tasks/',
            headers={
                'Authorization': valid_auth_token
            },
            json={
                'contents': todo_task_content
            }
        )
        assert add_response.status_code == 200
        added_task = TODOTask.from_dict(add_response.get_json())
        assert added_task.contents == todo_task_content

        with self.get_tasks(client) as query_response:
            assert query_response.status_code == 200
            assert len(query_response.get_json()) == 1
            assert TODOTask.from_dict(query_response.get_json()[0]) == added_task

    def test_add_task_db_access_mocked(self, mocker: MockerFixture, client: FlaskClient, valid_auth_token) -> None:
        todo_task_content = 'lorem ipsum'
        expected_created_task = TODOTask(str(uuid.uuid4()), todo_task_content)

        mocked = mocker.patch('app.core.TODOTaskCore.add_task')
        mocked.return_value = expected_created_task

        add_response = client.post(
            '/api/v1/todo_tasks/',
            headers={
                'Authorization': valid_auth_token
            },
            json={
                'contents': todo_task_content
            }
        )
        assert add_response.status_code == 200
        added_task = TODOTask.from_dict(add_response.get_json())
        assert added_task == expected_created_task

    def test_add_task_no_auth_token(self, client: FlaskClient, valid_auth_token):
        add_response = client.post(
            '/api/v1/todo_tasks/',
            json={
                'contents': 'lorem ipsum'
            }
        )
        assert add_response.status_code == 401

    @staticmethod
    def get_tasks(client):
        response = client.get('/api/v1/todo_tasks/')
        return response
