import logging
from datetime import datetime, timedelta, timezone
from time import perf_counter

import pytest
from django.test import Client
from oauth2_provider.models import AccessToken, Application

from store_api.models import Product, Tag, User

logger = logging.getLogger(__name__)


@pytest.fixture()
def api_client() -> Client:
    """
    Fixture to provide an API client using JSON as default content-type
    :return: django.test.Client
    """
    return Client()


@pytest.fixture(scope="session")
def default_password() -> str:
    return "l33t!passwdzzz"


class UserFactory:
    def create(
        self,
        email: str,
        username: str,
        password: str,
        deleted: None | datetime = None,
        is_active: bool = True,
    ) -> User:
        return User.objects.create_user(
            email=email,
            username=username,
            password=password,
            deleted=deleted,
            is_active=is_active,
        )


class ProductFactory:
    def create(
        self,
        owner: User,
        title: str,
        description: str,
        price: str,
        state: str = Product.STATE_AVAILABLE,
        stock_available=1,
        deleted: None | datetime = None,
    ) -> Product:

        product = Product(
            owner_user=owner,
            state=state,
            title=title,
            description=description,
            price=price,
            deleted=deleted,
        )
        product.save()

        product.stock.create(available=stock_available)

        return product


@pytest.fixture
def product_factory() -> ProductFactory:
    return ProductFactory()


@pytest.fixture
def user_factory() -> UserFactory:
    return UserFactory()


# TODO check if this can be session scoped
@pytest.fixture
def default_user(user_factory: UserFactory, default_password: str) -> User:
    return user_factory.create(
        email="john.doe@test.com", username="john.doe", password=default_password
    )


@pytest.fixture
def default_staff_user(default_admin_password: str) -> User:
    return User.objects.create_user(
        email="staff@testserver.com",
        username="staff@testserver",
        password=default_admin_password,
        is_staff=True,
    )


@pytest.fixture
def default_deleted_user(user_factory: UserFactory, default_password: str) -> User:
    """
    A fixture depicting a user deleted 1 hour prior
    """
    return user_factory.create(
        email="john.doe@test.com",
        username="john.doe",
        password=default_password,
        deleted=datetime.now(timezone.utc) - timedelta(hours=1),
        is_active=False,
    )


@pytest.fixture(scope="session")
def default_admin_password() -> str:
    return "Divinity!Iam!"


@pytest.fixture(scope="session")
def default_oauth_app_client_id() -> str:
    return "magnificent-test-app"


@pytest.fixture(scope="session")
def default_oauth_app_client_secret() -> str:
    return "SuP3rSeKr3tz"


@pytest.fixture(scope="session")
def custom_admin_user(
    django_db_setup, django_db_blocker, default_admin_password: str
) -> User:
    with django_db_blocker.unblock():
        t1 = perf_counter()
        val = User.objects.create_user(
            email="admin@testserver.com",
            username="root@testserver",
            password=default_admin_password,
            is_superuser=True,
        )
        logger.info(f"admin_user took {perf_counter() - t1}")
        return val


@pytest.fixture(scope="session")
def default_oauth_app(
    django_db_setup,
    django_db_blocker,
    default_oauth_app_client_id: str,
    default_oauth_app_client_secret: str,
    custom_admin_user: User,
) -> Application:
    with django_db_blocker.unblock():
        t1 = perf_counter()
        val = Application.objects.create(
            client_id=default_oauth_app_client_id,
            name=default_oauth_app_client_id,
            user=custom_admin_user,
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
        self, user: User, oauth_app: Application, scope="read write"
    ) -> AccessToken:
        return AccessToken.objects.create(
            user=user,
            token=f"{user.username}-{datetime.now().isoformat()}-token",
            application=oauth_app,
            expires=datetime.now(timezone.utc) + timedelta(minutes=2),
            scope=scope,
        )

    def generate_expired_api_access_token(
        self,
        user: User,
        oauth_app: Application,
        scopes="read write",
        expired_by=timedelta(minutes=1),
    ) -> AccessToken:
        return AccessToken.objects.create(
            user=user,
            token="blahblahblah",
            application=oauth_app,
            expires=datetime.now(timezone.utc) - expired_by,
        )


@pytest.fixture()
def auth_actions():
    return AuthActions()


class TagFactory:
    def create(self, name, description) -> Tag:
        return Tag.objects.create(name=name, description=description)


@pytest.fixture()
def tag_factory():
    return TagFactory()
