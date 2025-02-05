import uuid

import pytest
from django.test import Client
from oauth2_provider.models import Application

from store_api.models import Order, OrderLineItem, Product
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

        order_line_items = list(
            OrderLineItem.objects.filter(order_id=order_id)
            .filter(product_id=product.id)
            .all()
        )
        assert order_line_items == [
            OrderLineItem(order=order, product=product, variant="default", quantity=1)
        ]

        product.refresh_from_db()
        assert product.state == Product.STATE_AVAILABLE
        assert list(
            product.stock.filter(variant="default").values("product_id", "available")
        ) == [{"product_id": product.id, "available": 0}]

    def test_orders_can_have_multiple_products_with_specific_quantities(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_oauth_app: Application,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        seller_user1 = user_factory.create("user1@user1.com", "user1", "easyPass")
        seller_user2 = user_factory.create("user2@user2.com", "user2", "L33tPasswd!")
        buyer_user = user_factory.create("user3@user3.com", "user3", "b786435")

        product1 = product_factory.create(
            owner=seller_user1,
            title="user1_product_1",
            description="cheap",
            price=1000,
            stock_available=2,
        )
        product2 = product_factory.create(
            owner=seller_user2,
            title="user1_product_2",
            description="expensive",
            price=25999,
            stock_available=7,
        )

        buyer_access_token = auth_actions.generate_api_access_token(
            buyer_user, default_oauth_app
        )

        response = api_client.post(
            "http://testserver/api/orders/",
            content_type="application/json",
            data={
                "products": [
                    {"id": str(product1.id), "variant": "default", "quantity": 2},
                    {"id": str(product2.id), "variant": "default", "quantity": 3},
                ]
            },
            headers={"Authorization": f"Bearer {buyer_access_token.token}"},
        )
        assert response.status_code == 201

        order_id = uuid.UUID(response.json()["id"])
        order = Order.objects.get(id=order_id)
        assert order.state == "PENDING"
        assert order.customer_id == buyer_user.id

        order_line_items = list(OrderLineItem.objects.filter(order_id=order_id).all())
        assert order_line_items == [
            OrderLineItem(order=order, product=product1, variant="default", quantity=2),
            OrderLineItem(order=order, product=product2, variant="default", quantity=3),
        ]

        product1.refresh_from_db()
        assert product1.state == Product.STATE_AVAILABLE
        assert list(
            product1.stock.filter(variant="default").values("product_id", "available")
        ) == [{"product_id": product1.id, "available": 0}]

        product2.refresh_from_db()
        assert product2.state == Product.STATE_AVAILABLE
        assert list(
            product2.stock.filter(variant="default").values("product_id", "available")
        ) == [{"product_id": product2.id, "available": 4}]

    def test_trying_to_make_orders_with_insufficient_stock_fails(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_oauth_app: Application,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        seller_user1 = user_factory.create("user1@user1.com", "user1", "easyPass")
        seller_user2 = user_factory.create("user2@user2.com", "user2", "L33tPasswd!")
        buyer_user = user_factory.create("user3@user3.com", "user3", "b786435")

        product1 = product_factory.create(
            owner=seller_user1,
            title="user1_product_1",
            description="cheap",
            price=1000,
            stock_available=2,
        )
        product2 = product_factory.create(
            owner=seller_user2,
            title="user1_product_2",
            description="expensive",
            price=25999,
            stock_available=7,
        )

        buyer_access_token = auth_actions.generate_api_access_token(
            buyer_user, default_oauth_app
        )

        response = api_client.post(
            "http://testserver/api/orders/",
            content_type="application/json",
            data={
                "products": [
                    {"id": str(product1.id), "variant": "default", "quantity": 3},
                    {"id": str(product2.id), "variant": "default", "quantity": 3},
                ]
            },
            headers={"Authorization": f"Bearer {buyer_access_token.token}"},
        )
        assert response.status_code == 400
        assert response.json() == {
            "error": f"available stock for product {product1.id} is less than desired amount"
        }

        # verify stocks have not been modified
        product1.refresh_from_db()
        assert product1.state == Product.STATE_AVAILABLE
        assert list(
            product1.stock.filter(variant="default").values("product_id", "available")
        ) == [{"product_id": product1.id, "available": 2}]

        product2.refresh_from_db()
        assert product2.state == Product.STATE_AVAILABLE
        assert list(
            product2.stock.filter(variant="default").values("product_id", "available")
        ) == [{"product_id": product2.id, "available": 7}]

    def test_attempting_to_create_orders_for_non_existing_products_results_in_error(
        self,
        api_client: Client,
        auth_actions: AuthActions,
        default_oauth_app: Application,
        user_factory: UserFactory,
    ):
        buyer_user = user_factory.create("user2@user2.com", "user2", "b786435")

        non_existing_product_id1 = uuid.uuid4()
        non_existing_product_id2 = uuid.uuid4()

        buyer_access_token = auth_actions.generate_api_access_token(
            buyer_user, default_oauth_app
        )

        response = api_client.post(
            "http://testserver/api/orders/",
            content_type="application/json",
            data={
                "products": [
                    {
                        "id": str(non_existing_product_id1),
                        "variant": "default",
                        "quantity": 1,
                    },
                    {
                        "id": str(non_existing_product_id2),
                        "variant": "default",
                        "quantity": 1,
                    },
                ]
            },
            headers={"Authorization": f"Bearer {buyer_access_token.token}"},
        )
        assert response.status_code == 400
        assert response.json() == {
            "error": "requested products and/or stock variants that do not exist",
            "detail": [str(non_existing_product_id1), str(non_existing_product_id2)],
        }


# TODO test_attempting_to_create_orders_for_non_existing_products_variants_results_in_error
# TODO make an order but is asking for deleted product
# TODO make an order with different variants
