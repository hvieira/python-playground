from datetime import datetime
from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flask_server.db import Base


class User(Base):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(nullable=False)


class UserToken(Base):
    __tablename__ = 'user_token'

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    token: Mapped[str] = mapped_column(primary_key=True)
    expiry: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=True), nullable=False)
    user: Mapped[User] = relationship(foreign_keys=[user_id])
