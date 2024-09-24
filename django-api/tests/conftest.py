from typing import Generator

import pytest
from oauth2_provider.models import Application
from rest_framework.test import RequestsClient

from store_api.models import User


@pytest.fixture()
def api_client() -> Generator[RequestsClient, None, None]:
    """
    Fixture to provide an API client
    :return: RequestsClient
    """
    yield RequestsClient()


@pytest.fixture()
def default_password() -> str:
    return "l33t!passwdzzz"


@pytest.fixture()
def default_user(default_password: str) -> Generator[User, None, None]:
    yield User.objects.create_user(
        email="john.doe@test.com", username="john.doe", password=default_password
    )


@pytest.fixture()
def default_admin_password() -> str:
    return "Divinity!Iam!"


@pytest.fixture()
def default_oauth_app_client_id() -> str:
    return "magnificent-test-app"


@pytest.fixture()
def default_oauth_app_client_secret() -> str:
    return "SuP3rSeKr3tz"


@pytest.fixture()
def admin_user(default_admin_password: str) -> Generator[User, None, None]:
    yield User.objects.create_user(
        email="admin@testserver.com",
        username="root@testserver",
        password=default_admin_password,
        is_superuser=True,
    )


@pytest.fixture()
def default_oauth_app(
    default_oauth_app_client_id: str,
    default_oauth_app_client_secret: str,
    admin_user: User,
) -> Generator[Application, None, None]:

    yield Application.objects.create(
        client_id=default_oauth_app_client_id,
        name=default_oauth_app_client_id,
        user=admin_user,
        client_type=Application.CLIENT_PUBLIC,
        authorization_grant_type=Application.GRANT_PASSWORD,
        client_secret=default_oauth_app_client_secret,
        redirect_uris=["http://testserver/nonexist/callback"],
        post_logout_redirect_uris=["http://testserver/nonexist/logout"],
    )
