import uuid
from app.models import TODOTask
from app.db import db_session


class TODOTaskStorage:

    def get_tasks(self) -> list[TODOTask]:
        pass

    def add_task(self, task: TODOTask) -> TODOTask:
        pass


class DBTODOTaskStorage(TODOTaskStorage):

    def get_tasks(self) -> list[TODOTask]:
        return TODOTask.query.all()

    def add_task(self, task: TODOTask) -> TODOTask:
        task.id = str(uuid.uuid4())

        with db_session().begin():
            db_session.add(task)

        return task
