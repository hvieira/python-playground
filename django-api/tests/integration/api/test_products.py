import pytest
from django.test import Client
from oauth2_provider.models import Application

from store_api.models import User
from tests.conftest import AuthActions


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
