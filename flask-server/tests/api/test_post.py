from datetime import datetime
from flask import Flask
from flask.testing import FlaskClient

from tests.conftest import AuthActions


def test_api_get_posts_requires_non_expired_token(client: FlaskClient, app: Flask, auth: AuthActions):
    with app.app_context():
        auth.register()
        token = auth.create_api_token(app, expiry=datetime.min)

        response = client.get('/api/posts', 
                   headers={
                       'Authorization': f'Bearer {token}'
                   })
        
        assert response.status_code == 401


def test_api_get_posts_no_posts(client: FlaskClient, app: Flask, auth: AuthActions):
    with app.app_context():
        auth.register()
        token = auth.create_api_token(app)

        response = client.get('/api/posts', 
                   headers={
                       'Authorization': f'Bearer {token}'
                   })
        
        assert response.status_code == 200
        assert response.json == []

# TODO test pagination
# TODO test invalid token
# TODO test no token
# TODO test create post
# TODO test update post
# TODO test delete post