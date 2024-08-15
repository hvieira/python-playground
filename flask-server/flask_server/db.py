import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy import text
from flask import current_app, g


class Base(DeclarativeBase):
  pass


dbAlchemy = SQLAlchemy(model_class=Base)
