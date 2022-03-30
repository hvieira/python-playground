from typing import Optional, Mapping, Any
from flask import Flask

from kata import config, db
from kata.api import users


def create_app(test_config: Optional[Mapping[str, Any]] = None):
    app: Flask = Flask(__name__, instance_relative_config=True)

    init_schema = False
    if test_config is None:
        app.config.from_mapping(config.configuration_mapping)
    else:
        init_schema = True
        app.config.from_mapping(test_config)

    db.init(app, init_schema)

    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Hello, World!'

    app.register_blueprint(users.bp)

    return app
