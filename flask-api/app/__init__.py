from flask import Flask

from app import (
    config,
    db,
    core,
)
from app.resources import (
    auth, todo_task
)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    init_db = False
    if test_config is None:
        app.config.from_mapping(config.configuration_mapping)
    else:
        app.config.from_mapping(test_config)
        init_db = True

    db.configure(app, init_db)

    todo_core = core.TODOTaskCore()

    app.before_request(auth.load_logged_in_user)
    app.register_blueprint(todo_task.create_blueprint(todo_core))

    return app
