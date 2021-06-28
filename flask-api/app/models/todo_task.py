from sqlalchemy import Column,  String, Text
from sqlalchemy_serializer import SerializerMixin
from app.db import Base


class TODOTask(Base, SerializerMixin):
    __tablename__ = 'todo_task'
    id = Column(String(36), primary_key=True)
    contents = Column(Text)

    def __init__(self, todo_task_id, contents):
        self.id = todo_task_id
        self.contents = contents
