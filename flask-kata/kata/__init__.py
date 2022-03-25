import os
from typing import Optional, Mapping, Any

from flask import Flask


def create_app(test_config: Optional[Mapping[str, Any]] = None):
    app = Flask(__name__, instance_relative_config=True)

    # TODO will need to bootstrap this properly
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )

    if test_config is None:
        # TODO load config properly
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Hello, World!'

    # TODO load blueprints

    return app