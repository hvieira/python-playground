import pytest
from django.test import Client
from django.utils import timezone
from oauth2_provider.models import Application

from store_api.models import Product
from tests.conftest import AuthActions, ProductFactory, TagFactory, UserFactory


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
        )

        product_2 = product_factory.create(
            owner=user1,
            title="user1_product_2",
            description="expensive",
            price=50000,
            available_stock={"default": 3},
        )

        product_3 = product_factory.create(
            owner=user2,
            title="user2_product",
            description="user2_product_description",
            price=709,
            available_stock={"default": 7},
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
                        "default": 7,
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
                        "default": 3,
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
                        "default": 1,
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
                        "default": 1,
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
        )

        product_2 = product_factory.create(
            owner=user1,
            title="user1_product_2",
            description="expensive",
            price=50000,
            available_stock={"default": 3},
        )

        product_3 = product_factory.create(
            owner=user2,
            title="user2_product",
            description="user2_product_description",
            price=709,
            available_stock={"default": 7},
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
                        "default": 7,
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
                        "default": 3,
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
                        "default": 1,
                    },
                    "tags": [],
                },
            ],
        }

    def test_get_products_by_search_term_returns_relevant_results_using_title_description_and_tags(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_oauth_app: Application,
        user_factory: UserFactory,
        product_factory: ProductFactory,
        tag_factory: TagFactory,
    ):
        user1 = user_factory.create("user1@user1.com", "user1", "easyPass")
        user2 = user_factory.create("user2@user2.com", "user2", "b786435")
        user3 = user_factory.create("user3@user3.com", "user3", "n0v8e7ryt9t!")

        beauty_tag = tag_factory.create("beauty", "Beauty products")
        food_tag = tag_factory.create("food", "Food products")
        white_tag = tag_factory.create("white", "Products that are white")
        red_tag = tag_factory.create("red", "Products that are red")
        unique_tag = tag_factory.create("unique", "Unique products")

        red_lipstick = product_factory.create(
            owner=user1,
            title="red lipstick makeup",
            description="red lipstick to look sharp every day",
            price=1003,
            available_stock={"default": 3},
        )
        red_lipstick.tags.set([beauty_tag, red_tag])

        ramen_noodles = product_factory.create(
            owner=user1,
            title="ramen noodles",
            description="These noodles will be amazing in any ramen broth",
            price=50000,
            available_stock={"default": 12},
        )
        ramen_noodles.tags.set([food_tag, white_tag])

        red_unique_cap = product_factory.create(
            owner=user2,
            title="cap for yo head",
            description="Wearing this unique cap will make your coolness level over 9000!",
            price=709,
        )
        red_unique_cap.tags.set([red_tag, unique_tag])

        user3_access_token = auth_actions.generate_api_access_token(
            user3, default_oauth_app
        )

        request_page_size = 2
        response = api_client.get(
            "http://testserver/api/products/",
            query_params={"search_term": "noodles", "page_size": request_page_size},
            headers={"Authorization": f"Bearer {user3_access_token.token}"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "metadata": {
                "page_size": request_page_size,
                "offset_date": ramen_noodles.updated.isoformat().replace("+00:00", "Z"),
                "has_next": False,
            },
            "data": [
                {
                    "id": str(ramen_noodles.id),
                    "owner_user_id": str(ramen_noodles.owner_user.id),
                    "title": ramen_noodles.title,
                    "description": ramen_noodles.description,
                    "price": ramen_noodles.price,
                    "stock": {
                        "default": 12,
                    },
                    # TODO use serializers to transform the py objects to dicts to simplify and reduce code
                    "tags": [
                        {
                            "id": str(food_tag.id),
                            "name": food_tag.name,
                            "description": food_tag.description,
                        },
                        {
                            "id": str(white_tag.id),
                            "name": white_tag.name,
                            "description": white_tag.description,
                        },
                    ],
                },
            ],
        }

        response = api_client.get(
            "http://testserver/api/products/",
            query_params={"search_term": "red", "page_size": request_page_size},
            headers={"Authorization": f"Bearer {user3_access_token.token}"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "metadata": {
                "page_size": request_page_size,
                "offset_date": red_lipstick.updated.isoformat().replace("+00:00", "Z"),
                "has_next": False,
            },
            "data": [
                {
                    "id": str(red_unique_cap.id),
                    "owner_user_id": str(red_unique_cap.owner_user.id),
                    "title": red_unique_cap.title,
                    "description": red_unique_cap.description,
                    "price": red_unique_cap.price,
                    "stock": {
                        "default": 1,
                    },
                    "tags": [
                        {
                            "id": str(red_tag.id),
                            "name": red_tag.name,
                            "description": red_tag.description,
                        },
                        {
                            "id": str(unique_tag.id),
                            "name": unique_tag.name,
                            "description": unique_tag.description,
                        },
                    ],
                },
                {
                    "id": str(red_lipstick.id),
                    "owner_user_id": str(red_lipstick.owner_user.id),
                    "title": red_lipstick.title,
                    "description": red_lipstick.description,
                    "price": red_lipstick.price,
                    "stock": {
                        "default": 3,
                    },
                    "tags": [
                        {
                            "id": str(beauty_tag.id),
                            "name": beauty_tag.name,
                            "description": beauty_tag.description,
                        },
                        {
                            "id": str(red_tag.id),
                            "name": red_tag.name,
                            "description": red_tag.description,
                        },
                    ],
                },
            ],
        }

    # TODO (optional) test paging going back. likely needs a "forward" offset and a "backwards" offset
