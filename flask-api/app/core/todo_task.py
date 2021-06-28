from app.models import TODOTask


class TODOTaskCore:

    def retrieve_todo_tasks(self):
        return TODOTask.query.all()
