import datetime
from unittest.mock import MagicMock, patch
from flask import Flask
from flask.testing import FlaskClient
from freezegun import freeze_time
from flask_server.models.user import User, UserToken
from flask_server.db import dbAlchemy
from sqlalchemy import select


@freeze_time('2024-08-13 12:17:11', tz_offset=0)
@patch('random.choices')
def test_get_oauth_token_password_grant(rnd_choices_mock: MagicMock,  
                                        client: FlaskClient, 
                                        app: Flask):
    user = User(username='hugo', password='test')
    expected_token = 'blahblahblahblah'
    rnd_choices_mock.return_value = list(expected_token)

    with app.app_context():
        dbAlchemy.session.add(user)
        dbAlchemy.session.commit()
        dbAlchemy.session.flush()

        response = client.post('/oauth/token', json={
            'grant_type': 'password',
            'username': user.username,
            'password': user.password,
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


# TODO test client id
# TODO test client secret
# TODO test with user not existing
# TODO test with wrong credentials
# TODO test bad request

# TODO when using token, check for expiry

