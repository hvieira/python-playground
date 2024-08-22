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

    from .db import dbAlchemy
    dbAlchemy.init_app(app)

    from flask_server.json_encoding import ma
    ma.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    from flask_server.api import auth, post
    app.register_blueprint(auth.bp)
    app.register_blueprint(post.bp, url_prefix='/api')

    return app