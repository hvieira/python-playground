from unittest.mock import patch
from freezegun import freeze_time
import pytest

from requests import Response
from rest_framework.test import RequestsClient

from store_api.models import User


default_api_token = 'afs!vydu3kse$n12t0BGILAo&ANSD/Faj1hg#sfd'


@pytest.mark.django_db(transaction=True)
class TestUserAPITokens():

    @freeze_time('2024-08-13 12:17:11', tz_offset=0)
    @patch('random.choices', default_api_token)
    def test_create_get_token_for_user(self, api_client: RequestsClient, default_user: User, default_password: str):
        response: Response = api_client.post(
            'http://testserver/api/oauth/token',
            data = {
                'grant_type': 'password',
                'username': default_user.username,
                'password': default_password,
                # TODO These are not used but part of the request (client id & secret would differ per environment and should be configurable)
                'client_id': 'xxxxxxxxxx',
                'client_secret':'xxxxxxxxxx'
            }
        )
        
        assert response.status_code == 200
        assert response.json() == {
            'access_token': default_api_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
        }
