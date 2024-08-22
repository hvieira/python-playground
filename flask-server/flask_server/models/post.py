from sqlalchemy import TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flask_server.db import Base
from flask_server.models.user import User
from datetime import datetime

class Post(Base):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    created: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=True), default=func.current_timestamp())
    title: Mapped[str]
    body: Mapped[str]
    author: Mapped[User] = relationship(foreign_keys=[author_id])
    