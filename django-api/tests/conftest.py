import logging
from datetime import datetime, timedelta, timezone
from time import perf_counter
from typing import Generator

import pytest
from django.test import Client
from oauth2_provider.models import AccessToken, Application

from store_api.models import User

logger = logging.getLogger(__name__)


@pytest.fixture
def api_client() -> Client:
    """
    Fixture to provide an API client using JSON as default content-type
    :return: django.test.Client
    """
    return Client(headers={"Content-Type": "application/json"})


@pytest.fixture(scope="session")
def default_password() -> str:
    return "l33t!passwdzzz"


# TODO this probably should be a factory function
@pytest.fixture
def default_user(db, default_password: str) -> Generator[User, None, None]:
    t1 = perf_counter()
    val = User.objects.create_user(
        email="john.doe@test.com", username="john.doe", password=default_password
    )
    logger.info(f"default_user took {perf_counter() - t1}")
    return val


@pytest.fixture(scope="session")
def default_admin_password() -> str:
    return "Divinity!Iam!"


@pytest.fixture(scope="session")
def default_oauth_app_client_id() -> str:
    return "magnificent-test-app"


@pytest.fixture(scope="session")
def default_oauth_app_client_secret() -> str:
    return "SuP3rSeKr3tz"


@pytest.fixture
def custom_admin_user(db, default_admin_password: str) -> User:
    t1 = perf_counter()
    val = User.objects.create_user(
        email="admin@testserver.com",
        username="root@testserver",
        password=default_admin_password,
        is_superuser=True,
    )
    logger.info(f"admin_user took {perf_counter() - t1}")
    return val


@pytest.fixture
def default_oauth_app(
    default_oauth_app_client_id: str,
    default_oauth_app_client_secret: str,
    admin_user: User,
) -> Application:
    t1 = perf_counter()
    val = Application.objects.create(
        client_id=default_oauth_app_client_id,
        name=default_oauth_app_client_id,
        user=admin_user,
        client_type=Application.CLIENT_PUBLIC,
        authorization_grant_type=Application.GRANT_PASSWORD,
        client_secret=default_oauth_app_client_secret,
        redirect_uris=["http://testserver/nonexist/callback"],
        post_logout_redirect_uris=["http://testserver/nonexist/logout"],
    )
    logger.info(f"default_oauth_app took {perf_counter() - t1}")
    return val


class AuthActions:

    def generate_api_access_token(
        self, user: User, oauth_app: Application, scopes="read write"
    ) -> AccessToken:
        return AccessToken.objects.create(
            user=user,
            token="blahblahblah",
            application=oauth_app,
            expires=datetime.now(timezone.utc) + timedelta(minutes=2),
        )


@pytest.fixture()
def auth_actions():
    return AuthActions()
