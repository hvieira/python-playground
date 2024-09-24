from unittest.mock import patch
import pytest

from requests import Response
from rest_framework.test import RequestsClient
from oauth2_provider.models import Application

from store_api.models import User


default_api_token = 'afs!vydu3kse$n12t0BGILAo&ANSD/Faj1hg#sfd'
default_api_refresh_token = 'bbbbbbbbbbbbbbbbbbbbbbbbb'


@pytest.mark.django_db(transaction=True)
class TestUserAPITokens():

    @patch('oauthlib.oauth2.rfc6749.tokens.random_token_generator')
    def test_create_get_token_for_user(self,
                                       _random_token_generator,
                                       api_client: RequestsClient,
                                       default_user: User,
                                       default_password: str,
                                       default_oauth_app: Application,
                                       default_oauth_app_client_secret: str
                                       ):

        _random_token_generator.side_effect = [
            default_api_token,
            default_api_refresh_token
        ]

        response: Response = api_client.post(
            'https://testserver/oauth/token/',
            data = {
                'grant_type': 'password',
                'username': default_user.username,
                'password': default_password,
                'client_id': default_oauth_app.client_id,
                'client_secret': default_oauth_app_client_secret
            },
            allow_redirects = False
        )

        assert response.status_code == 200
        assert response.json() == {
            'access_token': default_api_token,
            'refresh_token': default_api_refresh_token,
            'expires_in': 36000,
            'token_type': 'Bearer',
            'scope': 'read write'
        }
