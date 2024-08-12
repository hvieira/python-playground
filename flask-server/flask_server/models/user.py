from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from flask_server.db import dbAlchemy

class User(dbAlchemy.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
