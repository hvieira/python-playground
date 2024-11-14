import uuid
from uuid import UUID

import pytest
from django.test import Client
from oauth2_provider.models import Application

from store_api.models import Product, User
from tests.conftest import AuthActions, ProductFactory, UserFactory


@pytest.mark.django_db()
class TestUserApi:

    def test_create_product(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_user: User,
        default_oauth_app: Application,
    ):
        product_title = "Amazing Product!"
        product_description = f"""This can only be found in {default_user.username} store.
        An amazing item that is now available to all!"""
        product_price = 7990
        product_stock = 7

        access_token = auth_actions.generate_api_access_token(
            default_user, default_oauth_app
        )

        response = api_client.post(
            "http://testserver/api/products/",
            content_type="application/json",
            data={
                "title": product_title,
                "description": product_description,
                "price": product_price,
                "available_stock": product_stock,
            },
            headers={"Authorization": f"Bearer {access_token.token}"},
        )

        assert response.status_code == 201

        assert response.json()["id"]
        assigned_product_id = response.json()["id"]
        assert response.json() == {
            "id": assigned_product_id,
            "owner_user_id": str(default_user.id),
            "title": product_title,
            "description": product_description,
            "price": product_price,
            "stock": {
                "default": {
                    "available": product_stock,
                    "reserved": 0,
                    "sold": 0,
                }
            },
        }

        product_in_db = Product.objects.get(id=assigned_product_id)
        assert product_in_db == Product(
            id=UUID(assigned_product_id),
            title=product_title,
            description=product_description,
            price=product_price,
            owner_user=default_user,
        )
        assert list(
            product_in_db.stock.all().values("variant", "available", "reserved", "sold")
        ) == [
            {
                "variant": "default",
                "available": product_stock,
                "reserved": 0,
                "sold": 0,
            }
        ]

    @pytest.mark.parametrize(
        "bad_request_body",
        [
            {
                "title": "product_title",
                "description": "product_description",
                "price": 100,
            },
            {
                "title": "product_title",
                "description": "product_description",
                "available_stock": 7,
            },
            {
                "title": "product_title",
                "price": 100,
                "available_stock": 7,
            },
            {
                "description": "product_description",
                "price": 100,
                "available_stock": 7,
            },
            # product cannot have price less or equal to zero
            {
                "title": "product_title",
                "description": "product_description",
                "price": 0,
                "available_stock": 1,
            },
            {
                "title": "product_title",
                "description": "product_description",
                "price": -1,
                "available_stock": 1,
            },
            # product cannot have negative stock
            {
                "title": "product_title",
                "description": "product_description",
                "price": 100,
                "available_stock": -1,
            },
        ],
    )
    def test_create_product_malformed_request(
        self,
        bad_request_body,
        api_client: Client,
        auth_actions: AuthActions,
        default_user: User,
        default_oauth_app: Application,
    ):
        access_token = auth_actions.generate_api_access_token(
            default_user, default_oauth_app
        )

        response = api_client.post(
            "http://testserver/api/products/",
            content_type="application/json",
            data=bad_request_body,
            headers={"Authorization": f"Bearer {access_token.token}"},
        )

        assert response.status_code == 400
        assert Product.objects.count() == 0

    def test_create_product_requires_credentials(
        self,
        api_client: Client,
    ):

        response = api_client.post(
            "http://testserver/api/products/",
            content_type="application/json",
            data={
                "title": "Amazing Product!",
                "description": "product_description",
                "price": 4000,
                "available_stock": 3,
            },
        )

        assert response.status_code == 401
        assert Product.objects.count() == 0

    def test_update_product(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_user: User,
        default_oauth_app: Application,
        product_factory: ProductFactory,
    ):
        new_product_title = "Amazing Product!"
        new_product_description = f"""This can only be found in {default_user.username} store.
        An amazing item that is now available to all!"""
        new_product_price = 7990
        new_product_stock = 7

        product = product_factory.create(
            default_user,
            "old_product_title",
            "old_product_description",
            1003,
            3,
            stock_reserved=1,
            stock_sold=71,
        )

        access_token = auth_actions.generate_api_access_token(
            default_user, default_oauth_app
        )

        response = api_client.put(
            f"http://testserver/api/products/{str(product.id)}/",
            content_type="application/json",
            data={
                "title": new_product_title,
                "description": new_product_description,
                "price": new_product_price,
                "available_stock": new_product_stock,
            },
            headers={"Authorization": f"Bearer {access_token.token}"},
        )

        assert response.status_code == 200

        assert response.json() == {
            "id": str(product.id),
            "owner_user_id": str(default_user.id),
            "title": new_product_title,
            "description": new_product_description,
            "price": new_product_price,
            "stock": {
                "default": {
                    "available": new_product_stock,
                    "reserved": 1,
                    "sold": 71,
                }
            },
        }

        product_in_db = Product.objects.get(id=product.id)
        assert product_in_db == Product(
            id=product.id,
            title=new_product_title,
            description=new_product_description,
            price=new_product_price,
            owner_user=default_user,
        )
        assert list(
            product_in_db.stock.all().values("variant", "available", "reserved", "sold")
        ) == [
            {
                "variant": "default",
                "available": new_product_stock,
                "reserved": 1,
                "sold": 71,
            }
        ]

    def test_users_cannot_update_other_users_products(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_oauth_app: Application,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        user1 = user_factory.create("user1@user1.com", "user1", "easyPass")
        user2 = user_factory.create("user2@user2.com", "user2", "easyPass")

        user1_product = product_factory.create(
            owner=user1,
            title="user1_product",
            description="user1_product_description",
            price=1003,
        )

        user2_product = product_factory.create(
            owner=user2,
            title="user2_product",
            description="user2_product_description",
            price=709,
        )

        malicious_update_request_body = {
            "title": "bad product",
            "description": "this product is a scam",
            "price": 1,
            "available_stock": 0,
        }

        user1_access_token = auth_actions.generate_api_access_token(
            user1, default_oauth_app
        )

        response = api_client.put(
            f"http://testserver/api/products/{str(user2_product.id)}/",
            content_type="application/json",
            data=malicious_update_request_body,
            headers={"Authorization": f"Bearer {user1_access_token.token}"},
        )
        assert response.status_code == 403

        user2_access_token = auth_actions.generate_api_access_token(
            user2, default_oauth_app
        )

        response = api_client.put(
            f"http://testserver/api/products/{str(user1_product.id)}/",
            content_type="application/json",
            data=malicious_update_request_body,
            headers={"Authorization": f"Bearer {user2_access_token.token}"},
        )
        assert response.status_code == 403

    def test_update_non_existing_product(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_user: User,
        default_oauth_app: Application,
    ):
        access_token = auth_actions.generate_api_access_token(
            default_user, default_oauth_app
        )

        response = api_client.put(
            f"http://testserver/api/products/{str(uuid.uuid4())}/",
            content_type="application/json",
            data={
                "title": "new_product_title",
                "description": "new_product_description",
                "price": 10000,
                "available_stock": 71,
            },
            headers={"Authorization": f"Bearer {access_token.token}"},
        )

        assert response.status_code == 404

    def test_users_can_delete_their_own_products(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_oauth_app: Application,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        user1 = user_factory.create("user1@user1.com", "user1", "easyPass")
        user2 = user_factory.create("user2@user2.com", "user2", "easyPass")

        user1_product = product_factory.create(
            owner=user1,
            title="user1_product",
            description="user1_product_description",
            price=1003,
        )

        user2_product = product_factory.create(
            owner=user2,
            title="user2_product",
            description="user2_product_description",
            price=709,
        )

        user1_access_token = auth_actions.generate_api_access_token(
            user1, default_oauth_app
        )

        response = api_client.delete(
            f"http://testserver/api/products/{str(user1_product.id)}/",
            headers={"Authorization": f"Bearer {user1_access_token.token}"},
        )
        assert response.status_code == 204

        response = api_client.delete(
            f"http://testserver/api/products/{str(user2_product.id)}/",
            content_type="application/json",
            headers={"Authorization": f"Bearer {user1_access_token.token}"},
        )
        assert response.status_code == 403


# TODO search/query for products do not return deleted products
