# TODO replace with "from typing import Self" with python 3.11
from __future__ import annotations
from datetime import datetime, timezone, timedelta
import random
import string
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
    created: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=True), nullable=False)
    expiry: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=True), nullable=False)
    user: Mapped[User] = relationship(foreign_keys=[user_id])

    # TODO configure expiry_seconds from a config key
    @staticmethod
    def create(user_id: int, duration_seconds=3600) -> UserToken:
        token = ''.join(random.choices(string.ascii_letters, k=20))
        now = datetime.now(timezone.utc)
        return UserToken(
            user_id=user_id, 
            token=token, 
            created=now,
            expiry=now + timedelta(seconds=duration_seconds)
        )
