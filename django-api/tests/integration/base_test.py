import logging

import pytest
from oauth2_provider.models import Application

from store_api.models import User


class BaseIntegrationTest:

    logger = logging.getLogger(__name__)

    custom_admin_user: User = None
    oauth_app: Application = None

    @pytest.fixture(autouse=True, scope="class")
    def prepare(
        self,
        django_db_blocker,
        default_admin_password,
        default_oauth_app_client_id,
        default_oauth_app_client_secret,
    ):

        django_db_blocker.unblock()
        # the admin_user fixture is function scoped, so create an admin
        self.custom_admin = User.objects.create_user(
            email="admin@testserver.com",
            username="root@testserver",
            password=default_admin_password,
            is_superuser=True,
        )

        self.oauth_app = Application.objects.create(
            client_id=default_oauth_app_client_id,
            name=default_oauth_app_client_id,
            user=self.custom_admin_user,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_PASSWORD,
            client_secret=default_oauth_app_client_secret,
            redirect_uris=["http://testserver/nonexist/callback"],
            post_logout_redirect_uris=["http://testserver/nonexist/logout"],
        )

        self.logger.info(self.oauth_app)
