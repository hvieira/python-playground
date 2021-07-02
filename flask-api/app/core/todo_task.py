from app.adapters import TODOTaskStorage
from app.models import TODOTask


class TODOTaskCore:

    def __init__(self, storage: TODOTaskStorage) -> None:
        self.storage = storage

    def retrieve_todo_tasks(self) -> list[TODOTask]:
        return self.storage.get_tasks()

    def add_task(self, task: TODOTask) -> TODOTask:
        return self.storage.add_task(task)
