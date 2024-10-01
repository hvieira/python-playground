import uuid
from typing import Callable

import pytest
from django.contrib.auth.hashers import check_password
from django.test import Client
from oauth2_provider.models import Application
from requests import Response

from store_api.models import User
from tests.conftest import AuthActions


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

    @pytest.mark.parametrize(
        "request_body",
        [
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@test.com",
                "username": "jane.doe",
            },
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@test.com",
                "password": "l33tPasswd",
            },
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "username": "jane.doe",
                "password": "l33tPasswd",
            },
            {
                "first_name": "Jane",
                "email": "jane.doe@test.com",
                "username": "jane.doe",
                "password": "l33tPasswd",
            },
            {
                "last_name": "Doe",
                "email": "jane.doe@test.com",
                "username": "jane.doe",
                "password": "l33tPasswd",
            },
            {
                "username": "suzuki",
                "email": "suzuki@notexist.com",
                "passwod": "pass123",
            },
            {},
        ],
    )
    def test_create_user_invalid_request(self, api_client: Client, request_body):
        response = api_client.post(
            "http://testserver/api/users/",
            data=request_body,
        )

        assert response.status_code == 400
        assert User.objects.count() == 0

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

    def test_update_password_needs_correct_old_password(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_user: User,
        default_password,
        default_oauth_app: Application,
    ):
        new_password = "Ch3ckITOuT!"

        access_token = auth_actions.generate_api_access_token(
            default_user, default_oauth_app
        )

        response: Response = api_client.post(
            f"http://testserver/api/users/{default_user.id}/update-password/",
            data={
                "old_password": "wrongPassWord",
                "new_password": new_password,
            },
            headers={"Authorization": f"Bearer {access_token.token}"},
        )

        assert response.status_code == 400

        # make sure that the password did not change
        default_user.refresh_from_db()
        assert check_password(default_password, default_user.password)

    @pytest.mark.parametrize(
        "request_body",
        [
            {"old_password": "old", "password": "new"},
            {"old_password": "old"},
            {
                "new_password": "new",
            },
            {},
        ],
    )
    def test_update_password_invalid_request_body(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_user: User,
        default_password,
        default_oauth_app: Application,
        request_body,
    ):
        access_token = auth_actions.generate_api_access_token(
            default_user, default_oauth_app
        )

        response: Response = api_client.post(
            f"http://testserver/api/users/{default_user.id}/update-password/",
            data=request_body,
            headers={"Authorization": f"Bearer {access_token.token}"},
        )

        assert response.status_code == 400

        # make sure that the password did not change
        default_user.refresh_from_db()
        assert check_password(default_password, default_user.password)

    def test_update_password_no_access_token(
        self,
        api_client: Client,
        default_user: User,
        default_password,
    ):
        new_password = "Ch3ckITOuT!"

        response: Response = api_client.post(
            f"http://testserver/api/users/{default_user.id}/update-password/",
            data={
                "old_password": default_password,
                "new_password": new_password,
            },
        )

        assert response.status_code == 401

        # make sure that the password did not change
        default_user.refresh_from_db()
        assert check_password(default_password, default_user.password)

    def test_update_password_invalid_access_token(
        self,
        api_client: Client,
        default_user: User,
        default_password,
    ):
        new_password = "Ch3ckITOuT!"

        response: Response = api_client.post(
            f"http://testserver/api/users/{default_user.id}/update-password/",
            data={
                "old_password": default_password,
                "new_password": new_password,
            },
            headers={"Authorization": "Bearer letMeIn"},
        )

        assert response.status_code == 401

        # make sure that the password did not change
        default_user.refresh_from_db()
        assert check_password(default_password, default_user.password)

    def test_update_password_expired_access_token(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_user: User,
        default_password,
        default_oauth_app: Application,
    ):
        new_password = "Ch3ckITOuT!"

        access_token = auth_actions.generate_expired_api_access_token(
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

        assert response.status_code == 401

        # make sure that the password did not change
        default_user.refresh_from_db()
        assert check_password(default_password, default_user.password)

    def test_update_password_cannot_do_that_for_another_user(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        user_factory: Callable[[], User],
        default_oauth_app: Application,
    ):
        new_password = "password_wanted_to_be_set_by_user1"

        user1_password = "stronkPassW"
        user2_password = "weak&vulnerable"

        user1 = user_factory(
            email="user1@mailzzz.com", username="user1", password=user1_password
        )
        user2 = user_factory(
            email="user2@mailzzz.com", username="user2", password=user2_password
        )

        user1_access_token = auth_actions.generate_expired_api_access_token(
            user1, default_oauth_app
        )

        response: Response = api_client.post(
            f"http://testserver/api/users/{user2.id}/update-password/",
            data={
                "old_password": user2_password,
                "new_password": new_password,
            },
            headers={"Authorization": f"Bearer {user1_access_token.token}"},
        )

        assert response.status_code == 401

        # make sure that the password did not change
        user1.refresh_from_db()
        user2.refresh_from_db()
        assert check_password(user1_password, user1.password)
        assert check_password(user2_password, user2.password)
