from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flask_server.db import dbAlchemy
from flask_server.models.user import User
from datetime import datetime


class Post(dbAlchemy.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    created: Mapped[datetime] = mapped_column(default=func.current_timestamp())
    title: Mapped[str]
    body: Mapped[str]
    author: Mapped[User] = relationship()
