from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

db_session = scoped_session(sessionmaker())

Base = declarative_base()
Base.query = db_session.query_property()


def configure(app, init_db):
    engine = create_engine(app.config['DATABASE_URL'])
    db_session.configure(
        autocommit=False,
        autoflush=False,
        bind=engine)

    if init_db:
        Base.metadata.create_all(engine)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()
