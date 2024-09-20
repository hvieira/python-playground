import uuid
import pytest

from django.contrib.auth.hashers import check_password
from rest_framework.test import RequestsClient

from store_api.models import User


# TODO for some reason need to mark this as a transaction
# follow issue - https://github.com/pytest-dev/pytest-django/issues/1099
@pytest.mark.django_db(transaction=True)
class TestUserApi():

    def test_create_user(self, api_client: RequestsClient):
        first_name = 'John'
        last_name = 'Lastest'
        email = 'john.latest@test.com'
        username = 'john.latest'
        password = 'superSecr3tz'

        response = api_client.post(
            'http://testserver/api/users/',
            data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'username': username,
                'password': password
            }
        )

        assert response.status_code == 201

        assert User.objects.count() == 1
        user =  User.objects.first() 
        assert user
        assert user.id
        assert user.first_name == first_name
        assert user.last_name == last_name
        assert user.username == username
        assert user.email == email
        assert check_password(password, user.password)
        

# TODO test malformed request
# TODO test no request body
