import uuid

import pytest

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


class TestTODOTaskResource:

    def test_list_items(self, client, some_todo_tasks):
        response = client.get('/api/v1/todo_tasks/')

        assert response.status_code == 200
        assert response.get_json() == [i.to_dict() for i in some_todo_tasks]
