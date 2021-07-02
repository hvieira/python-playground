import functools

from flask import (
    Response,
    g,
    request,
    abort,
    current_app
)


def load_logged_in_user():
    auth_token = request.headers.get('Authorization', None)
    g.client_auth_token = auth_token


def authenticated_client(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.client_auth_token is None:
            current_app.logger.warning("Request made without authentication to protected resource")
            abort(Response("Request requires authentication", status=401))
        else:
            # validation of token would happen here
            return view(**kwargs)

    return wrapped_view
