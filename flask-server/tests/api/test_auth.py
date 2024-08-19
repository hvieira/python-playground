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


@freeze_time('2024-08-13 12:17:11', tz_offset=0)
@patch('random.choices')
def test_get_oauth_token_password_grant(rnd_choices_mock: MagicMock,  
                                        client: FlaskClient, 
                                        app: Flask):
    plain_passwd = 'testzzz'
    user = User(username='hugo', password=generate_password_hash(plain_passwd))
    expected_token = 'blahblahblahblah'
    rnd_choices_mock.return_value = list(expected_token)

    with app.app_context():
        dbAlchemy.session.add(user)
        dbAlchemy.session.commit()
        dbAlchemy.session.flush()

        response = client.post('/oauth/token', json={
            'grant_type': 'password',
            'username': user.username,
            'password': plain_passwd,
            'client_id': 'test',
            'client_secret': 'bananas'
        })

        assert response.status_code == 200
        assert response.json == {
            'access_token': expected_token,
            'token_type': 'Bearer',
            'expires_in': 60 * 60,
        }

        user1Tokens = dbAlchemy.session.execute(select(UserToken).where(UserToken.user_id == user.id)).scalars().all()
        assert len(user1Tokens) == 1
        assert user1Tokens[0].user_id == user.id
        assert user1Tokens[0].token == expected_token
        assert user1Tokens[0].expiry == datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=1)


def test_get_oauth_token_password_non_existing_user(client: FlaskClient):
    response = client.post('/oauth/token', json={
        'grant_type': 'password',
        'username': 'do not exist',
        'password': 'do not exist passwd',
        'client_id': 'test',
        'client_secret': 'bananas'
    })

    assert response.status_code == 401


def test_get_oauth_token_password_wrong_credentials(client: FlaskClient, app: Flask):
    user = User(username='hugo', password='test')
    with app.app_context():
        dbAlchemy.session.add(user)
        dbAlchemy.session.commit()
        dbAlchemy.session.flush()
    
        response = client.post('/oauth/token', json={
            'grant_type': 'password',
            'username': user.username,
            'password': 'wrong!',
            'client_id': 'test',
            'client_secret': 'bananas'
        })

        assert response.status_code == 401


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
    ]
)
def test_get_oauth_token_password_non_existing_user(client: FlaskClient, bad_token_request):
    assert client.post('/oauth/token', json=bad_token_request).status_code == 400


# TODO test client id
# TODO test client secret
# TODO when using token, check for expiry

