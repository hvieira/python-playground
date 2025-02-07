import uuid

import pytest
from django.contrib.auth.hashers import check_password
from django.test import Client
from oauth2_provider.models import AccessToken, Application

from store_api.models import User
from tests.conftest import AuthActions, UserFactory


@pytest.mark.django_db()
class TestUserAPI:

    def test_create_user(self, api_client: Client):
        first_name = "John"
        last_name = "Lastest"
        email = "john.latest@test.com"
        username = "john.latest"
        password = "superSecr3tz"

        response = api_client.post(
            "http://testserver/api/users/",
            content_type="application/json",
            data={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "username": username,
                "password": password,
            },
        )

        assert response.status_code == 201
        user_queryset = (
            User.objects.filter(first_name=first_name)
            .filter(last_name=last_name)
            .filter(username=username)
            .filter(email=email)
        )
        assert user_queryset.count() == 1
        user_from_db = user_queryset.first()
        assert type(user_from_db.id) is uuid.UUID
        assert user_from_db.first_name == first_name
        assert user_from_db.last_name == last_name
        assert user_from_db.username == username
        assert user_from_db.email == email
        assert check_password(password, user_from_db.password)

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
            content_type="application/json",
            data=request_body,
        )

        assert response.status_code == 400

    def test_update_existing_user_password(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        user_factory: UserFactory,
        default_oauth_app: Application,
    ):
        old_password = "Oldy!$"
        new_password = "Ch3ckITOuT!"

        user = user_factory.create("test@test.com", "userz", old_password)

        access_token = auth_actions.generate_api_access_token(user, default_oauth_app)

        response = api_client.post(
            f"http://testserver/api/users/{user.id}/update-password/",
            content_type="application/json",
            data={
                "old_password": old_password,
                "new_password": new_password,
            },
            headers={"Authorization": f"Bearer {access_token.token}"},
        )

        assert response.status_code == 204

        user.refresh_from_db()
        assert check_password(new_password, user.password)

    def test_update_password_needs_correct_old_password(
        self,
        api_client: Client,
        default_user: User,
        default_password,
        default_user_long_lived_access_token: AccessToken,
    ):
        new_password = "Ch3ckITOuT!"

        response = api_client.post(
            f"http://testserver/api/users/{default_user.id}/update-password/",
            content_type="application/json",
            data={
                "old_password": "wrongPassWord",
                "new_password": new_password,
            },
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
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
        default_user: User,
        default_password: str,
        default_user_long_lived_access_token: AccessToken,
        request_body: dict,
    ):
        response = api_client.post(
            f"http://testserver/api/users/{default_user.id}/update-password/",
            content_type="application/json",
            data=request_body,
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )

        assert response.status_code == 400

        # make sure that the password did not change
        default_user.refresh_from_db()
        assert check_password(default_password, default_user.password)

    def test_update_password_no_access_token(
        self,
        api_client: Client,
        default_user: User,
        default_password: str,
    ):
        new_password = "Ch3ckITOuT!"

        response = api_client.post(
            f"http://testserver/api/users/{default_user.id}/update-password/",
            content_type="application/json",
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
        default_password: str,
    ):
        new_password = "Ch3ckITOuT!"

        response = api_client.post(
            f"http://testserver/api/users/{default_user.id}/update-password/",
            content_type="application/json",
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
        default_password: str,
        default_oauth_app: Application,
    ):
        new_password = "Ch3ckITOuT!"

        access_token = auth_actions.generate_expired_api_access_token(
            default_user, default_oauth_app
        )

        response = api_client.post(
            f"http://testserver/api/users/{default_user.id}/update-password/",
            content_type="application/json",
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
        user_factory: UserFactory,
        default_oauth_app: Application,
    ):
        new_password = "password_wanted_to_be_set_by_user1"

        user1_password = "stronkPassW"
        user2_password = "weak&vulnerable"

        user1 = user_factory.create(
            email="user1@mailzzz.com", username="user1", password=user1_password
        )
        user2 = user_factory.create(
            email="user2@mailzzz.com", username="user2", password=user2_password
        )

        user1_access_token = auth_actions.generate_expired_api_access_token(
            user1, default_oauth_app
        )

        response = api_client.post(
            f"http://testserver/api/users/{user2.id}/update-password/",
            content_type="application/json",
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

    def test_get_user_public_profile(
        self,
        api_client: Client,
        user_factory: UserFactory,
        default_oauth_app: Application,
        auth_actions: AuthActions,
    ):
        user1_password = "stronkPassW"
        user2_password = "weak&vulnerable"
        user1: User = user_factory.create(
            email="user1@mailzzz.com", username="user1", password=user1_password
        )
        user2 = user_factory.create(
            email="user2@mailzzz.com", username="user2", password=user2_password
        )

        user1_access_token = auth_actions.generate_api_access_token(
            user1, default_oauth_app
        )
        user2_access_token = auth_actions.generate_api_access_token(
            user2, default_oauth_app
        )

        # user1 can see user2 public profile
        response = api_client.get(
            f"http://testserver/api/users/{user2.id}/",
            headers={"Authorization": f"Bearer {user1_access_token.token}"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "username": user2.username,
            "date_joined": user2.date_joined.isoformat().replace(
                "+00:00", "Z"
            ),  # TODO find a better to handle this
        }

        # user2 can see user1 public profile
        response = api_client.get(
            f"http://testserver/api/users/{user1.id}/",
            headers={"Authorization": f"Bearer {user2_access_token.token}"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "username": user1.username,
            "date_joined": user1.date_joined.isoformat().replace(
                "+00:00", "Z"
            ),  # TODO find a better to handle this
        }

    def test_get_user_public_profile_needs_valid_access_token(
        self,
        api_client: Client,
        user_factory: UserFactory,
        default_oauth_app: Application,
        auth_actions: AuthActions,
    ):
        user1_password = "stronkPassW"
        user2_password = "weak&vulnerable"
        user1: User = user_factory.create(
            email="user1@mailzzz.com", username="user1", password=user1_password
        )
        user2 = user_factory.create(
            email="user2@mailzzz.com", username="user2", password=user2_password
        )

        # user1 attempts to see user2 public profile
        response = api_client.get(f"http://testserver/api/users/{user2.id}/")
        assert response.status_code == 401

        response = api_client.get(
            f"http://testserver/api/users/{user2.id}/",
            headers={"Authorization": "Bearer blah"},
        )
        assert response.status_code == 401

        expired_access_token = auth_actions.generate_expired_api_access_token(
            user1, default_oauth_app
        )
        response = api_client.get(
            f"http://testserver/api/users/{user2.id}/",
            headers={"Authorization": f"Bearer {expired_access_token.token}"},
        )
        assert response.status_code == 401

    def test_get_user_own_profile(
        self,
        api_client: Client,
        default_user: User,
        default_user_long_lived_access_token: AccessToken,
    ):
        response = api_client.get(
            f"http://testserver/api/users/{default_user.id}/",
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "first_name": default_user.first_name,
            "last_name": default_user.last_name,
            "username": default_user.username,
            "email": default_user.email,
            "date_joined": default_user.date_joined.isoformat().replace(
                "+00:00", "Z"
            ),  # TODO find a better to handle this
        }
