from __future__ import annotations
from typing import cast
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

    def __eq__(self, o: object) -> bool:
        if type(o) is TODOTask:
            other = cast(TODOTask, o)
            return (
                self.id == other.id
                and self.contents == other.contents
            )
        else:
            return False

    @staticmethod
    def from_dict(src: dict) -> TODOTask:
        return TODOTask(
            src.get('id'),
            src['contents']
        )

