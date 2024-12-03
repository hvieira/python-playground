from uuid import UUID

import pytest
from django.test import Client
from oauth2_provider.models import Application

from store_api.models import Tag, User
from tests.conftest import AuthActions

CREATE_TAG_PAYLOAD = {
    "name": "beautiful",
    "description": "Tagged entity is deemed beautiful",
}


@pytest.mark.django_db()
class TestTagAPI:

    def test_staff_users_can_create_tags(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_staff_user: User,
        default_oauth_app: Application,
    ):
        access_token = auth_actions.generate_api_access_token(
            default_staff_user, default_oauth_app
        )

        response = api_client.post(
            "http://testserver/api/tags/",
            content_type="application/json",
            data=CREATE_TAG_PAYLOAD,
            headers={"Authorization": f"Bearer {access_token.token}"},
        )

        # TODO standardize returned status code to 201 when entities/resources are created
        assert response.status_code == 201
        assert response.json()["id"] is not None
        assert UUID(response.json()["id"])

        assigned_id = response.json()["id"]
        assert response.json() == {
            "id": assigned_id,
            "name": CREATE_TAG_PAYLOAD["name"],
            "description": CREATE_TAG_PAYLOAD["description"],
        }

        assert Tag.objects.get(id=assigned_id) == Tag(
            id=UUID(assigned_id),
            name=CREATE_TAG_PAYLOAD["name"],
            description=CREATE_TAG_PAYLOAD["description"],
        )

    def test_non_staff_users_cannot_create_tags(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_user: User,
        default_oauth_app: Application,
    ):
        access_token = auth_actions.generate_api_access_token(
            default_user, default_oauth_app
        )

        response = api_client.post(
            "http://testserver/api/tags/",
            content_type="application/json",
            data=CREATE_TAG_PAYLOAD,
            headers={"Authorization": f"Bearer {access_token.token}"},
        )

        assert response.status_code == 403

    # TODO staff user can list tags

    # TODO staff user can update tag names

    # TODO staff user can HEAD tags (check a tag exists)

    # TODO staff user can delete tags (an unassociate all products using it)
