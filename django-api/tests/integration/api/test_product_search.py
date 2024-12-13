import pytest
from django.test import Client
from django.utils import timezone
from oauth2_provider.models import Application

from store_api.models import Product
from tests.conftest import AuthActions, ProductFactory, UserFactory


@pytest.mark.django_db()
class TestProductSearchAPI:

    def test_get_products_returns_paged_list_newest_first(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_oauth_app: Application,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        user1 = user_factory.create("user1@user1.com", "user1", "easyPass")
        user2 = user_factory.create("user2@user2.com", "user2", "b786435")
        user3 = user_factory.create("user3@user3.com", "user3", "n0v8e7ryt9t!")

        product_1 = product_factory.create(
            owner=user1,
            title="user1_product_1",
            description="cheap",
            price=1003,
            stock_available=1,
        )

        product_2 = product_factory.create(
            owner=user1,
            title="user1_product_2",
            description="expensive",
            price=50000,
            stock_available=3,
        )

        product_3 = product_factory.create(
            owner=user2,
            title="user2_product",
            description="user2_product_description",
            price=709,
            stock_available=7,
        )

        user3_access_token = auth_actions.generate_api_access_token(
            user3, default_oauth_app
        )

        response = api_client.get(
            "http://testserver/api/products/",
            content_type="application/json",
            headers={"Authorization": f"Bearer {user3_access_token.token}"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "metadata": {
                "page_size": 20,
                "offset_date": product_1.updated.isoformat().replace("+00:00", "Z"),
                "has_next": False,
            },
            "data": [
                {
                    "id": str(product_3.id),
                    "owner_user_id": str(product_3.owner_user.id),
                    "title": product_3.title,
                    "description": product_3.description,
                    "price": product_3.price,
                    "stock": {
                        "default": {
                            "available": 7,
                            "reserved": 0,
                            "sold": 0,
                        }
                    },
                    "tags": [],
                },
                {
                    "id": str(product_2.id),
                    "owner_user_id": str(product_2.owner_user.id),
                    "title": product_2.title,
                    "description": product_2.description,
                    "price": product_2.price,
                    "stock": {
                        "default": {
                            "available": 3,
                            "reserved": 0,
                            "sold": 0,
                        }
                    },
                    "tags": [],
                },
                {
                    "id": str(product_1.id),
                    "owner_user_id": str(product_1.owner_user.id),
                    "title": product_1.title,
                    "description": product_1.description,
                    "price": product_1.price,
                    "stock": {
                        "default": {
                            "available": 1,
                            "reserved": 0,
                            "sold": 0,
                        }
                    },
                    "tags": [],
                },
            ],
        }

    def test_get_products_does_not_return_deleted_products(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_oauth_app: Application,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        user1 = user_factory.create("user1@user1.com", "user1", "easyPass")
        user3 = user_factory.create("user3@user3.com", "user3", "n0v8e7ryt9t!")

        product_1 = product_factory.create(
            owner=user1,
            title="user1_product_1",
            description="cheap",
            price=1003,
            stock_available=1,
        )

        product_factory.create(
            owner=user1,
            title="user1_product_2",
            description="expensive",
            price=50000,
            state=Product.STATE_DELETED,
            deleted=timezone.now(),
        )

        user3_access_token = auth_actions.generate_api_access_token(
            user3, default_oauth_app
        )

        response = api_client.get(
            "http://testserver/api/products/",
            content_type="application/json",
            headers={"Authorization": f"Bearer {user3_access_token.token}"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "metadata": {
                "page_size": 20,
                "offset_date": product_1.updated.isoformat().replace("+00:00", "Z"),
                "has_next": False,
            },
            "data": [
                {
                    "id": str(product_1.id),
                    "owner_user_id": str(product_1.owner_user.id),
                    "title": product_1.title,
                    "description": product_1.description,
                    "price": product_1.price,
                    "stock": {
                        "default": {
                            "available": 1,
                            "reserved": 0,
                            "sold": 0,
                        }
                    },
                    "tags": [],
                },
            ],
        }

    def test_get_products_returns_paging_usage(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_oauth_app: Application,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        user1 = user_factory.create("user1@user1.com", "user1", "easyPass")
        user2 = user_factory.create("user2@user2.com", "user2", "b786435")
        user3 = user_factory.create("user3@user3.com", "user3", "n0v8e7ryt9t!")

        product_1 = product_factory.create(
            owner=user1,
            title="user1_product_1",
            description="cheap",
            price=1003,
            stock_available=1,
        )

        product_2 = product_factory.create(
            owner=user1,
            title="user1_product_2",
            description="expensive",
            price=50000,
            stock_available=3,
        )

        product_3 = product_factory.create(
            owner=user2,
            title="user2_product",
            description="user2_product_description",
            price=709,
            stock_available=7,
        )

        user3_access_token = auth_actions.generate_api_access_token(
            user3, default_oauth_app
        )

        request_page_size = 2
        response = api_client.get(
            "http://testserver/api/products/",
            query_params={"page_size": request_page_size},
            content_type="application/json",
            headers={"Authorization": f"Bearer {user3_access_token.token}"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "metadata": {
                "page_size": request_page_size,
                "offset_date": product_2.updated.isoformat().replace("+00:00", "Z"),
                "has_next": True,
            },
            "data": [
                {
                    "id": str(product_3.id),
                    "owner_user_id": str(product_3.owner_user.id),
                    "title": product_3.title,
                    "description": product_3.description,
                    "price": product_3.price,
                    "stock": {
                        "default": {
                            "available": 7,
                            "reserved": 0,
                            "sold": 0,
                        }
                    },
                    "tags": [],
                },
                {
                    "id": str(product_2.id),
                    "owner_user_id": str(product_2.owner_user.id),
                    "title": product_2.title,
                    "description": product_2.description,
                    "price": product_2.price,
                    "stock": {
                        "default": {
                            "available": 3,
                            "reserved": 0,
                            "sold": 0,
                        }
                    },
                    "tags": [],
                },
            ],
        }

        # get 2nd page
        response = api_client.get(
            "http://testserver/api/products/",
            query_params={
                "page_size": request_page_size,
                "offset": product_2.updated.isoformat().replace("+00:00", "Z"),
            },
            content_type="application/json",
            headers={"Authorization": f"Bearer {user3_access_token.token}"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "metadata": {
                "page_size": request_page_size,
                "offset_date": product_1.updated.isoformat().replace("+00:00", "Z"),
                "has_next": False,
            },
            "data": [
                {
                    "id": str(product_1.id),
                    "owner_user_id": str(product_1.owner_user.id),
                    "title": product_1.title,
                    "description": product_1.description,
                    "price": product_1.price,
                    "stock": {
                        "default": {
                            "available": 1,
                            "reserved": 0,
                            "sold": 0,
                        }
                    },
                    "tags": [],
                },
            ],
        }

    # TODO search by a term will search title, description and tags (non deleted products and non deleted tags)

    # TODO (optional) test paging going back. likely needs a "forward" offset and a "backwards" offset
