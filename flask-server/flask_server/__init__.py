import os

from flask import Flask
from flask_server.config import Configuration, configuration

def create_app(test_config:Configuration = None):
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        app.config.from_object(configuration)
    else:
        app.config.from_object(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .db import dbAlchemy, init_db_command
    dbAlchemy.init_app(app)

    app.cli.add_command(init_db_command)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app