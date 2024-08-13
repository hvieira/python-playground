import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy import text
from flask import current_app, g


class Base(DeclarativeBase):
  pass


dbAlchemy = SQLAlchemy(model_class=Base)


def init_db():
    with dbAlchemy.engine.begin() as conn:
       conn.execute(text('DROP TABLE IF EXISTS post'))
       conn.execute(text('DROP TABLE IF EXISTS "user"'))
       conn.execute(text('''
CREATE TABLE "user" (
  id serial PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
)
'''))
       conn.execute(text('''
CREATE TABLE post (
  id serial PRIMARY KEY,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES "user" (id)
)
'''))

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')