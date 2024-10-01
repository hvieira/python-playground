import uuid

import pytest
from django.contrib.auth.hashers import check_password
from django.test import Client
from oauth2_provider.models import Application
from requests import Response

from store_api.models import User
from tests.conftest import AuthActions


# TODO for some reason need to mark this as a transaction
# follow issue - https://github.com/pytest-dev/pytest-django/issues/1099
@pytest.mark.django_db()
class TestUserApi:

    def test_create_user(self, api_client: Client):
        first_name = "John"
        last_name = "Lastest"
        email = "john.latest@test.com"
        username = "john.latest"
        password = "superSecr3tz"

        response = api_client.post(
            "http://testserver/api/users/",
            data={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "username": username,
                "password": password,
            },
        )

        assert response.status_code == 201

        assert User.objects.count() == 1
        user = User.objects.first()
        assert user
        assert type(user.id) is uuid.UUID
        assert user.first_name == first_name
        assert user.last_name == last_name
        assert user.username == username
        assert user.email == email
        assert check_password(password, user.password)

    # TODO test malformed request
    # TODO test no request body

    def test_update_existing_user_password(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_user: User,
        default_password: str,
        default_oauth_app: Application,
    ):
        new_password = "Ch3ckITOuT!"

        access_token = auth_actions.generate_api_access_token(
            default_user, default_oauth_app
        )

        response: Response = api_client.post(
            f"http://testserver/api/users/{default_user.id}/update-password/",
            data={
                "old_password": default_password,
                "new_password": new_password,
            },
            headers={"Authorization": f"Bearer {access_token.token}"},
        )

        assert response.status_code == 204

        default_user.refresh_from_db()
        assert check_password(new_password, default_user.password)

    # TODO test update password with wrong old password - bad request
    # TODO test update password with wrong request format(s)
    # TODO test update password with no token
    # TODO test update password with expired token
    # TODO test update password with invalid token
    # TODO cannot change another user's password
