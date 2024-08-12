from flask.testing import FlaskClient
import pytest
from flask import g, session
from flask_server.models.user import User
from flask_server.db import dbAlchemy
from sqlalchemy import select

def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        created_user = dbAlchemy.session.execute(select(User).where(User.username == 'a'))
        assert created_user is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data

def test_username_already_in_use(client: FlaskClient):
    response = client.post(
        '/auth/register',
        data={'username': 'test', 'password': 'test'}
    )
    assert response.status_code == 302
    
    response = client.post(
        '/auth/register',
        data={'username': 'test', 'password': 'test'}
    )
    assert b'already registered' in response.data

def test_login(client, auth):
    auth.register()
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user.username == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_wrong_credentials(auth, username, password, message):
    auth.register()
    response = auth.login(username, password)
    assert message in response.data