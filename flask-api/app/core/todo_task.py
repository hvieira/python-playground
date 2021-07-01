import uuid

from app.models import TODOTask

from app.db import db_session


class TODOTaskCore:

    def retrieve_todo_tasks(self):
        return TODOTask.query.all()

    def add_task(self, task: TODOTask) -> TODOTask:
        task.id = str(uuid.uuid4())

        db_session.add(task)
        db_session.commit()

        return task
