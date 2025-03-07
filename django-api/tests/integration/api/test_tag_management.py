import uuid
from uuid import UUID

import pytest
from django.test import Client
from oauth2_provider.models import AccessToken, Application

from store_api.models import Tag, User
from tests.conftest import AuthActions, TagFactory

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
        self, api_client: Client, default_user_long_lived_access_token: AccessToken
    ):
        response = api_client.post(
            "http://testserver/api/tags/",
            content_type="application/json",
            data=CREATE_TAG_PAYLOAD,
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )

        assert response.status_code == 403

    def test_authenticated_users_can_list_tags(
        self,
        api_client: Client,
        tag_factory: TagFactory,
        default_user_long_lived_access_token: AccessToken,
    ):
        tag1 = tag_factory.create("tag1", "tag1 description")
        tag2 = tag_factory.create("tag2", "tag2 description")

        response = api_client.get(
            "http://testserver/api/tags/",
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "metadata": {
                "page_size": 50,
                "offset_date": tag2.created.isoformat().replace("+00:00", "Z"),
                "has_next": False,
            },
            "data": [
                {
                    "id": str(tag1.id),
                    "name": tag1.name,
                    "description": tag1.description,
                },
                {
                    "id": str(tag2.id),
                    "name": tag2.name,
                    "description": tag2.description,
                },
            ],
        }

    def test_authenticated_users_can_list_tags_with_pagination(
        self,
        api_client: Client,
        tag_factory: TagFactory,
        default_user_long_lived_access_token: AccessToken,
    ):
        tag1 = tag_factory.create("tag1", "tag1 description")
        tag2 = tag_factory.create("tag2", "tag2 description")

        response = api_client.get(
            "http://testserver/api/tags/",
            query_params={
                "page_size": 1,
            },
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "metadata": {
                "page_size": 1,
                "offset_date": tag1.created.isoformat().replace("+00:00", "Z"),
                "has_next": True,
            },
            "data": [
                {
                    "id": str(tag1.id),
                    "name": tag1.name,
                    "description": tag1.description,
                },
            ],
        }

        response = api_client.get(
            "http://testserver/api/tags/",
            query_params={
                "page_size": 20,
                "offset": tag1.created.isoformat().replace("+00:00", "Z"),
            },
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "metadata": {
                "page_size": 20,
                "offset_date": tag2.created.isoformat().replace("+00:00", "Z"),
                "has_next": False,
            },
            "data": [
                {
                    "id": str(tag2.id),
                    "name": tag2.name,
                    "description": tag2.description,
                },
            ],
        }

    def test_authenticated_users_can_check_if_a_tag_exists(
        self,
        api_client: Client,
        tag_factory: TagFactory,
        default_user_long_lived_access_token: AccessToken,
    ):
        tag1 = tag_factory.create("tag1", "tag1 description")
        tag2 = tag_factory.create("tag2", "tag2 description")

        response = api_client.head(
            f"http://testserver/api/tags/{str(tag1.id)}/",
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )
        assert response.status_code == 200

        response = api_client.head(
            f"http://testserver/api/tags/{str(tag2.id)}/",
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )
        assert response.status_code == 200

        # check for a tag that does not exist
        response = api_client.head(
            f"http://testserver/api/tags/{str(uuid.uuid4())}/",
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )
        assert response.status_code == 404

    def test_authenticated_staff_users_can_update_tags(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_staff_user: User,
        default_oauth_app: Application,
        tag_factory: TagFactory,
    ):
        tag1 = tag_factory.create("tag1", "tag1 description")
        tag_new_name = "new"
        tag_new_description = "Depicts new items"

        access_token = auth_actions.generate_api_access_token(
            default_staff_user, default_oauth_app
        )

        response = api_client.put(
            f"http://testserver/api/tags/{str(tag1.id)}/",
            content_type="application/json",
            data={"name": tag_new_name, "description": tag_new_description},
            headers={"Authorization": f"Bearer {access_token.token}"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(tag1.id),
            "name": tag_new_name,
            "description": tag_new_description,
        }

        tag1.refresh_from_db()
        assert tag1.name == tag_new_name
        assert tag1.description == tag_new_description

    def test_non_staff_users_cannot_update_tags(
        self,
        api_client: Client,
        tag_factory: TagFactory,
        default_user_long_lived_access_token: AccessToken,
    ):
        tag1 = tag_factory.create("tag1", "tag1 description")
        tag_new_name = "new"
        tag_new_description = "Depicts new items"

        response = api_client.put(
            f"http://testserver/api/tags/{str(tag1.id)}/",
            content_type="application/json",
            data={"name": tag_new_name, "description": tag_new_description},
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )

        assert response.status_code == 403

    def test_authenticated_staff_users_can_delete_tags(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_staff_user: User,
        default_oauth_app: Application,
        tag_factory: TagFactory,
    ):
        tag1 = tag_factory.create("tag1", "tag1 description")

        access_token = auth_actions.generate_api_access_token(
            default_staff_user, default_oauth_app
        )

        response = api_client.delete(
            f"http://testserver/api/tags/{str(tag1.id)}/",
            content_type="application/json",
            headers={"Authorization": f"Bearer {access_token.token}"},
        )

        assert response.status_code == 204
        tag1.refresh_from_db()
        assert tag1.name == "tag1"
        assert tag1.description == "tag1 description"
        assert tag1.updated is not None

    def test_non_staff_users_cannot_delete_tags(
        self,
        api_client: Client,
        tag_factory: TagFactory,
        default_user_long_lived_access_token: AccessToken,
    ):
        tag1 = tag_factory.create("tag1", "tag1 description")

        response = api_client.delete(
            f"http://testserver/api/tags/{str(tag1.id)}/",
            content_type="application/json",
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )

        assert response.status_code == 403

    def test_users_can_search_for_tags_using_a_term(
        self,
        api_client: Client,
        tag_factory: TagFactory,
        default_user_long_lived_access_token: AccessToken,
    ):
        _ = tag_factory.create("beauty", "Beauty products")
        tag2 = tag_factory.create("fashion", "Fashion products")
        _ = tag_factory.create("food", "Food items")
        tag4 = tag_factory.create("fabulous", "Fabulous")

        response = api_client.get(
            "http://testserver/api/tags/",
            query_params={"search_term": "fa"},
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "metadata": {
                "page_size": 50,
                "offset_date": tag4.created.isoformat().replace("+00:00", "Z"),
                "has_next": False,
            },
            "data": [
                {
                    "id": str(tag2.id),
                    "name": tag2.name,
                    "description": tag2.description,
                },
                {
                    "id": str(tag4.id),
                    "name": tag4.name,
                    "description": tag4.description,
                },
            ],
        }
