from flask_sqlalchemy import SQLAlchemy


db: SQLAlchemy = SQLAlchemy()


def init(app, init_schema):
    db.init_app(app)

    if init_schema:
        print('Creating schema...')
        db.create_all(app=app)
        print('Created DB schema')

    return db
