from datetime import datetime
from flask import Flask
from flask.testing import FlaskClient
import pytest

from flask_server.models.post import Post
from tests.conftest import AuthActions, PostActions, serialize_dt_iso_format


def test_api_get_posts_requires_bearer_token(client: FlaskClient, app: Flask, auth: AuthActions):
    with app.app_context():
        auth.register()

        response = client.get('/api/posts')
        
        assert response.status_code == 401

@pytest.mark.parametrize(
        'authorization_header',
        [
            (''),
            ('X'),
            ('Bearer'),
            ('Bearer '),
            ('Bearer  '),
            ('Bearer XXX'),
        ]
)
def test_api_get_posts_does_not_accept_invalid_bearer_tokens(client: FlaskClient, app: Flask, auth: AuthActions, authorization_header):
    with app.app_context():
        auth.register()

        response = client.get('/api/posts', headers={'Authorization': authorization_header})
        
        assert response.status_code == 401

def test_api_get_posts_requires_non_expired_token(client: FlaskClient, app: Flask, auth: AuthActions):
    with app.app_context():
        auth.register()
        # TODO try having these as fixtures - the user, a valid token, an expired token (etc on other tests)
        token = auth.create_api_token(app, expiry=datetime.min)

        response = get_posts(client, token)
        
        assert response.status_code == 401


def test_api_get_posts_no_posts(client: FlaskClient, app: Flask, auth: AuthActions):
    with app.app_context():
        auth.register()
        token = auth.create_api_token(app)

        response = get_posts(client, token)
        
        assert response.status_code == 200
        assert response.json == []

def test_api_get_posts_pagination(client: FlaskClient, app: Flask, auth: AuthActions, posting: PostActions):
    with app.app_context() as ctx:

        auth.register()
        user = auth.get_user_from_username(app)

        post1 = Post(author_id=user.id, title='Hello', body='World!')
        post2 = Post(author_id=user.id, title='Lorem', body='Ipsum')
        post3 = Post(author_id=user.id, title='The World', body='''
The world is Fascinating
    But can be otherwise
        This is not rhyming
            So it's not wise
        ''')

        posting.create_post(post1)
        posting.create_post(post2)
        posting.create_post(post3)

        token = auth.create_api_token(app)
        
        response = get_posts(client, token)
        assert response.status_code == 200
        assert response.json == [
            _expected_post_json(post1),
            _expected_post_json(post2),
            _expected_post_json(post3),
        ]

        response = get_posts(client, token, {'page_size': 1, 'offset_cursor': 0})
        assert response.status_code == 200
        assert response.json == [
            _expected_post_json(post1),
        ]

        response = get_posts(client, token, {'page_size': 2, 'offset_cursor': 1})
        assert response.status_code == 200
        assert response.json == [
            _expected_post_json(post2),
            _expected_post_json(post3),
        ]

        response = get_posts(client, token, {'page_size': 2, 'offset_cursor': 3})
        assert response.status_code == 200
        assert response.json == []


def get_posts(client, token, query_string={}):
    return client.get(
        "/api/posts",
        headers={"Authorization": f"Bearer {token}"},
        query_string=query_string,
    )


def _expected_post_json(post: Post) -> dict:
    return {
        'id': post.id,
        'created': serialize_dt_iso_format(post.created),
        'author': {
            'id':  post.author.id,
            'username':  post.author.username
        },
        'title': post.title,
        'body': post.body
    }

# TODO test create post
# TODO test update post
# TODO test delete post
