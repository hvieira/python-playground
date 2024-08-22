from marshmallow_sqlalchemy import auto_field
from sqlalchemy import TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flask_server.db import Base
from flask_server.models.user import User, UserJson
from flask_server.json_encoding import ma
from datetime import datetime
from marshmallow_sqlalchemy.fields import Nested

class Post(Base):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    created: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=True), default=func.current_timestamp())
    title: Mapped[str]
    body: Mapped[str]
    author: Mapped[User] = relationship(foreign_keys=[author_id])

    # TODO use a mixin for this, or find a lib to handle this - of course the need to hide certain fields is necessary
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'author_id': self.author_id,
            'created': self.created,
            'title': self.title,
            'body': self.body,
        }
    

class PostJson(ma.SQLAlchemySchema):
    class Meta:
        model = Post

    id = ma.auto_field()
    created = ma.auto_field()
    title = ma.auto_field()
    body = ma.auto_field()
    author = Nested(UserJson)

post_json = PostJson()
post_json_list = PostJson(many=True)