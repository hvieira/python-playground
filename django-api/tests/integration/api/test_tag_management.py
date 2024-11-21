from uuid import UUID

import pytest
from django.test import Client
from oauth2_provider.models import Application

from store_api.models import User
from tests.conftest import AuthActions


@pytest.mark.django_db()
class TestTagAPI:

    def test_staff_users_can_create_tags(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_staff_user: User,
        default_oauth_app: Application,
    ):
        payload = {
            "name": "beautiful",
            "description": "Tagged entity is deemed beautiful",
        }

        access_token = auth_actions.generate_api_access_token(
            default_staff_user, default_oauth_app
        )

        response = api_client.post(
            "http://testserver/api/tags/",
            content_type="application/json",
            data=payload,
            headers={"Authorization": f"Bearer {access_token.token}"},
        )

        # TODO standardize returned status code to 201 when entities/resources are created
        assert response.status_code == 201
        assert response.json()["id"] is not None
        assert UUID(response.json()["id"])

        assigned_id = response.json()["id"]
        assert response.json() == {
            "id": assigned_id,
            "name": "beautiful",
            "description": "Tagged entity is deemed beautiful",
        }

    # TODO staff user can list tags

    # TODO staff user can update tag names

    # TODO staff user can HEAD tags (check a tag exists)

    # TODO staff user can delete tags (an unassociate all products using it)
