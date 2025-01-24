import uuid

import pytest
from django.test import Client
from oauth2_provider.models import Application

from store_api.models import Order, Product
from tests.conftest import AuthActions, ProductFactory, UserFactory


@pytest.mark.django_db()
class TestOrder:

    def test_created_orders_are_placed_in_pending(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_oauth_app: Application,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        seller_user = user_factory.create("user1@user1.com", "user1", "easyPass")
        buyer_user = user_factory.create("user2@user2.com", "user2", "b786435")

        product = product_factory.create(
            owner=seller_user,
            title="user1_product_1",
            description="cheap",
            price=1003,
            stock_available=1,
        )

        request_payload = {
            "products": [{"id": str(product.id), "variant": "default", "quantity": 1}]
        }

        buyer_access_token = auth_actions.generate_api_access_token(
            buyer_user, default_oauth_app
        )

        response = api_client.post(
            "http://testserver/api/orders/",
            content_type="application/json",
            data=request_payload,
            headers={"Authorization": f"Bearer {buyer_access_token.token}"},
        )
        assert response.status_code == 201

        order_id = uuid.UUID(response.json()["id"])
        order = Order.objects.get(id=order_id)
        assert order.state == "PENDING"
        assert order.customer_id == buyer_user.id

        product.refresh_from_db()
        assert product.order_id == order_id
        assert product.state == Product.STATE_SOLD_OUT
        assert list(
            product.stock.filter(variant="default").values("product_id", "available")
        ) == [{"product_id": product.id, "available": 0}]


# TODO make an order with multiple products
# TODO make an order but there's not enough stock
# TODO make an order but is asking for non existing product(s)
# TODO make an order but is asking for deleted product
