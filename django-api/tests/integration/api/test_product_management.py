import uuid
from datetime import datetime
from uuid import UUID

import pytest
from django.test import Client
from oauth2_provider.models import Application

from store_api.models import Product, User
from tests.conftest import AuthActions, ProductFactory, TagFactory, UserFactory


@pytest.mark.django_db()
class TestProductManagementAPI:

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
                "stock": {"default": product_stock},
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
                "default": product_stock,
            },
            "tags": [],
        }

        product_in_db = Product.objects.get(id=assigned_product_id)
        assert product_in_db == Product(
            id=UUID(assigned_product_id),
            title=product_title,
            description=product_description,
            price=product_price,
            owner_user=default_user,
        )
        assert list(product_in_db.stock.all().values("variant", "available")) == [
            {
                "variant": "default",
                "available": product_stock,
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
                "stock": {"default": 7},
            },
            {
                "title": "product_title",
                "price": 100,
                "stock": {"default": 7},
            },
            {
                "description": "product_description",
                "price": 100,
                "stock": {"default": 7},
            },
            # product cannot have price less or equal to zero
            {
                "title": "product_title",
                "description": "product_description",
                "price": 0,
                "stock": {"default": 7},
            },
            {
                "title": "product_title",
                "description": "product_description",
                "price": -1,
                "stock": {"default": 7},
            },
            # product cannot have negative stock
            {
                "title": "product_title",
                "description": "product_description",
                "price": 100,
                "stock": {"default": -1},
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

        product = product_factory.create(
            owner=default_user,
            title="old_product_title",
            description="old_product_description",
            price=1003,
            available_stock={"default": 3, "silver": 4},
        )

        product_that_should_not_change = product_factory.create(
            owner=default_user,
            title="trousers",
            description="regular",
            price=1003,
            available_stock={"default": 3, "silver": 4, "xl": 3, "s": 4},
        )
        product_that_should_not_change_original_update_time = (
            product_that_should_not_change.updated
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
                "stock": {"default": 7, "gold": 3},
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
            "stock": {"default": 7, "gold": 3},
            "tags": [],
        }

        product_in_db = Product.objects.get(id=product.id)
        assert product_in_db == Product(
            id=product.id,
            title=new_product_title,
            description=new_product_description,
            price=new_product_price,
            owner_user=default_user,
        )
        assert list(product_in_db.stock.all().values("variant", "available")) == [
            {
                "variant": "default",
                "available": 7,
            },
            {
                "variant": "gold",
                "available": 3,
            },
        ]

        # verify that other products have not changed
        product_that_should_not_change.refresh_from_db()
        assert (
            product_that_should_not_change.updated
            == product_that_should_not_change_original_update_time
        )
        assert list(
            product_that_should_not_change.stock.all().values("variant", "available")
        ) == [
            {
                "variant": "default",
                "available": 3,
            },
            {
                "variant": "silver",
                "available": 4,
            },
            {
                "variant": "xl",
                "available": 3,
            },
            {
                "variant": "s",
                "available": 4,
            },
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
            "stock": {"default": 0},
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
                "stock": {"default": 71},
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
        user2_product_original_stock = list(user2_product.stock.all())

        user1_access_token = auth_actions.generate_api_access_token(
            user1, default_oauth_app
        )

        response = api_client.delete(
            f"http://testserver/api/products/{str(user1_product.id)}/",
            headers={"Authorization": f"Bearer {user1_access_token.token}"},
        )
        assert response.status_code == 204

        user1_product.refresh_from_db()
        assert user1_product.state == Product.STATE_DELETED
        assert user1_product.deleted is not None
        assert type(user1_product.deleted) is datetime
        assert user1_product.stock.all().count() == 0

        # cannot deleted other users products
        response = api_client.delete(
            f"http://testserver/api/products/{str(user2_product.id)}/",
            headers={"Authorization": f"Bearer {user1_access_token.token}"},
        )
        assert response.status_code == 403

        user2_product.refresh_from_db()
        assert user2_product.state == Product.STATE_AVAILABLE
        assert list(user2_product.stock.all()) == user2_product_original_stock
        assert user2_product.deleted is None

    def test_create_product_with_tags(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_user: User,
        default_oauth_app: Application,
        tag_factory: TagFactory,
    ):
        product_title = "Amazing Product!"
        product_description = f"""This can only be found in {default_user.username} store.
        An amazing item that is now available to all!"""
        product_price = 19900
        product_stock = 3

        unique_tag = tag_factory.create("unique", "Unique products")
        glamourous_tag = tag_factory.create("glamourous", "Glamour related products")

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
                "stock": {"default": product_stock},
                "tags": [
                    str(unique_tag.id),
                    str(glamourous_tag.id),
                ],
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
                "default": product_stock,
            },
            "tags": [
                {
                    "id": str(unique_tag.id),
                    "name": unique_tag.name,
                    "description": unique_tag.description,
                },
                {
                    "id": str(glamourous_tag.id),
                    "name": glamourous_tag.name,
                    "description": glamourous_tag.description,
                },
            ],
        }

        created_product_from_db = Product.objects.get(id=assigned_product_id)
        assert list(created_product_from_db.tags.all()) == [unique_tag, glamourous_tag]

    def test_update_product_with_tags(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_user: User,
        default_oauth_app: Application,
        product_factory: ProductFactory,
        tag_factory: TagFactory,
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
            available_stock={"default": 3},
        )

        unique_tag = tag_factory.create("unique", "Unique products")
        glamourous_tag = tag_factory.create("glamourous", "Glamour related products")

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
                "stock": {"default": new_product_stock},
                "tags": [
                    str(unique_tag.id),
                    str(glamourous_tag.id),
                ],
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
                "default": new_product_stock,
            },
            "tags": [
                {
                    "id": str(unique_tag.id),
                    "name": unique_tag.name,
                    "description": unique_tag.description,
                },
                {
                    "id": str(glamourous_tag.id),
                    "name": glamourous_tag.name,
                    "description": glamourous_tag.description,
                },
            ],
        }

        product_in_db = Product.objects.get(id=product.id)
        assert product_in_db == Product(
            id=product.id,
            title=new_product_title,
            description=new_product_description,
            price=new_product_price,
            owner_user=default_user,
        )
        assert list(product_in_db.stock.all().values("variant", "available")) == [
            {
                "variant": "default",
                "available": new_product_stock,
            }
        ]
        assert list(product_in_db.tags.all()) == [unique_tag, glamourous_tag]

    def test_update_product_replace_tags(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_user: User,
        default_oauth_app: Application,
        product_factory: ProductFactory,
        tag_factory: TagFactory,
    ):
        product = product_factory.create(
            default_user,
            "product_title",
            "product_description",
            1003,
            available_stock={"default": 3},
        )

        unique_tag = tag_factory.create("unique", "Unique products")
        glamourous_tag = tag_factory.create("glamourous", "Glamour related products")

        product.tags.add(unique_tag)

        access_token = auth_actions.generate_api_access_token(
            default_user, default_oauth_app
        )

        response = api_client.put(
            f"http://testserver/api/products/{str(product.id)}/",
            content_type="application/json",
            data={
                "title": product.title,
                "description": product.description,
                "price": product.price,
                "stock": {"default": 1},
                "tags": [
                    str(glamourous_tag.id),
                ],
            },
            headers={"Authorization": f"Bearer {access_token.token}"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(product.id),
            "owner_user_id": str(default_user.id),
            "title": product.title,
            "description": product.description,
            "price": product.price,
            "stock": {
                "default": 1,
            },
            "tags": [
                {
                    "id": str(glamourous_tag.id),
                    "name": glamourous_tag.name,
                    "description": glamourous_tag.description,
                },
            ],
        }

        product_in_db = Product.objects.get(id=product.id)
        assert product_in_db == product
        assert list(product_in_db.stock.all().values("variant", "available")) == [
            {
                "variant": "default",
                "available": 1,
            }
        ]
        assert list(product_in_db.tags.all()) == [glamourous_tag]

    def test_create_product_with_multiple_variants(
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
        product_stock = 11

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
                "stock": {"default": product_stock},
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
                "default": product_stock,
            },
            "tags": [],
        }

        product_in_db = Product.objects.get(id=assigned_product_id)
        assert product_in_db == Product(
            id=UUID(assigned_product_id),
            title=product_title,
            description=product_description,
            price=product_price,
            owner_user=default_user,
        )
        assert list(product_in_db.stock.all().values("variant", "available")) == [
            {
                "variant": "default",
                "available": product_stock,
            }
        ]


# TODO test product create with non existing tag - results in 400 error
