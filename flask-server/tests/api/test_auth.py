import datetime
from unittest.mock import MagicMock, patch
from flask import Flask
from flask.testing import FlaskClient
from freezegun import freeze_time
import pytest
from flask_server.models.user import User, UserToken
from flask_server.db import dbAlchemy
from sqlalchemy import select
from werkzeug.security import generate_password_hash


###
# requirements/tests based on https://www.oauth.com/oauth2-servers/access-tokens/access-token-response/ 
###

@freeze_time('2024-08-13 12:17:11', tz_offset=0)
@patch('random.choices')
def test_get_oauth_token_password_grant(rnd_choices_mock: MagicMock,  
                                        client: FlaskClient, 
                                        app: Flask):
    plain_passwd = 'testzzz'
    user = User(username='hugo', password=generate_password_hash(plain_passwd))
    expected_token = 'blahblahblahblah'
    rnd_choices_mock.return_value = list(expected_token)

    with app.app_context() as ctx:
        dbAlchemy.session.add(user)
        dbAlchemy.session.commit()
        dbAlchemy.session.flush()

        response = client.post('/oauth/token', json={
            'grant_type': 'password',
            'username': user.username,
            'password': plain_passwd,
            "client_id": ctx.app.config.get('OAUTH_CLIENT_ID'),
            "client_secret": ctx.app.config.get('OAUTH_CLIENT_SECRET'),
        })

        assert response.status_code == 200
        assert response.json == {
            'access_token': expected_token,
            'token_type': 'Bearer',
            'expires_in': 60 * 60,
        }

        userTokens = dbAlchemy.session.execute(select(UserToken).where(UserToken.user_id == user.id)).scalars().all()
        assert len(userTokens) == 1
        assert userTokens[0].user_id == user.id
        assert userTokens[0].token == expected_token
        assert userTokens[0].expiry == datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=1)


def test_get_oauth_token_password_non_existing_user(client: FlaskClient, app: Flask):
    with app.app_context() as ctx:
        response = client.post('/oauth/token', json={
            'grant_type': 'password',
            'username': 'do not exist',
            'password': 'do not exist passwd',
            "client_id": ctx.app.config.get('OAUTH_CLIENT_ID'),
            "client_secret": ctx.app.config.get('OAUTH_CLIENT_SECRET'),
        })

        assert response.status_code == 400
        assert response.json == {'error': 'invalid_grant'}


def test_get_oauth_token_password_wrong_credentials(client: FlaskClient, app: Flask):
    user = User(username='hugo', password='test')
    with app.app_context() as ctx:
        dbAlchemy.session.add(user)
        dbAlchemy.session.commit()
        dbAlchemy.session.flush()
    
        response = client.post('/oauth/token', json={
            'grant_type': 'password',
            'username': user.username,
            'password': 'wrong!',
            "client_id": ctx.app.config.get('OAUTH_CLIENT_ID'),
            "client_secret": ctx.app.config.get('OAUTH_CLIENT_SECRET'),
        })

        
        assert response.status_code == 400
        assert response.json == {'error': 'invalid_grant'}


@pytest.mark.parametrize(
    'bad_token_request',
    [
        ({
            'username': 'user',
            'password': 'pass',
            'client_id': 'test',
            'client_secret': 'bananas'
        }),
        ({
            'grant_type': 'password',
            'password': 'pass',
            'client_id': 'test',
            'client_secret': 'bananas'
        }),
        ({
            'grant_type': 'password',
            'username': 'user',
            'client_id': 'test',
            'client_secret': 'bananas'
        }),
        ({
            'grant_type': 'password',
            'username': 'user',
            'password': 'pass',
            'client_secret': 'bananas'
        }),
        ({
            'grant_type': 'password',
            'username': 'user',
            'password': 'pass',
            'client_id': 'test',
        }),
        ({
            'grant_type': 'password',
            'username': 'user',
            'password': 'pass',
            'client_id': 'test',
        }),
        ({
            'lorem': 'ipsum'
        })
    ]
)
def test_get_oauth_token_password_non_existing_user(client: FlaskClient, bad_token_request):
    response = client.post('/oauth/token', json=bad_token_request)
    assert response.status_code == 400
    assert response.json == {'error': 'invalid_request'}

def test_get_oauth_token_unsupported_grant_type(client: FlaskClient, app: Flask):
    with app.app_context() as ctx:
        response = client.post(
            "/oauth/token",
            json={
                "grant_type": "client_credentials",
                "username": "user",
                "password": "passwd",
                "client_id": ctx.app.config.get('OAUTH_CLIENT_ID'),
                "client_secret": ctx.app.config.get('OAUTH_CLIENT_SECRET'),
            },
        )
        assert response.status_code == 400
        assert response.json == {
            'error': 'unsupported_grant_type'
        }

def test_get_oauth_token_wrong_client_id(client: FlaskClient, app: Flask):
    with app.app_context() as ctx:
        response = client.post(
            "/oauth/token",
            json={
                "grant_type": "password",
                "username": "user",
                "password": "passwd",
                "client_id": "doesnt_exist",
                "client_secret": ctx.app.config.get('OAUTH_CLIENT_SECRET'),
            },
        )
        assert response.status_code == 401
        assert response.json == {
            'error': 'invalid_client'
        }

def test_get_oauth_token_wrong_client_secret(client: FlaskClient, app: Flask):
    with app.app_context() as ctx:
        response = client.post(
            "/oauth/token",
            json={
                "grant_type": "password",
                "username": "user",
                "password": "passwd",
                "client_id": ctx.app.config.get('OAUTH_CLIENT_ID'),
                "client_secret": "bad_secret",
            },
        )

        assert response.status_code == 401
        assert response.json == {
            'error': 'invalid_client'
        }
