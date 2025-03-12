import uuid

import pytest
from django.test import Client
from django.utils import timezone
from oauth2_provider.models import AccessToken

from store_api.models import Order, OrderLineItem, Product, User
from tests.conftest import OrderFactory, ProductFactory, UserFactory


@pytest.mark.django_db()
class TestOrder:

    def test_created_orders_are_placed_in_pending(
        self,
        api_client: Client,
        default_user: User,
        default_user_long_lived_access_token: AccessToken,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        seller_user = user_factory.create("user1@user1.com", "user1", "easyPass")
        buyer_user = default_user

        product = product_factory.create(
            owner=seller_user,
            title="user1_product_1",
            description="cheap",
            price=1003,
        )

        request_payload = {
            "products": [{"id": str(product.id), "variant": "default", "quantity": 1}]
        }

        response = api_client.post(
            "http://testserver/api/orders/",
            content_type="application/json",
            data=request_payload,
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
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
        default_user: User,
        default_user_long_lived_access_token: AccessToken,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        seller_user1 = user_factory.create("user1@user1.com", "user1", "easyPass")
        seller_user2 = user_factory.create("user2@user2.com", "user2", "L33tPasswd!")
        buyer_user = default_user

        product1 = product_factory.create(
            owner=seller_user1,
            title="user1_product_1",
            description="cheap",
            price=1000,
            available_stock={"default": 2},
        )
        product2 = product_factory.create(
            owner=seller_user2,
            title="user1_product_2",
            description="expensive",
            price=25999,
            available_stock={"default": 7},
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
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
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
        default_user: User,
        default_user_long_lived_access_token: AccessToken,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        seller_user1 = user_factory.create("user1@user1.com", "user1", "easyPass")
        seller_user2 = user_factory.create("user2@user2.com", "user2", "L33tPasswd!")
        buyer = default_user

        product1 = product_factory.create(
            owner=seller_user1,
            title="user1_product_1",
            description="cheap",
            price=1000,
            available_stock={"default": 2},
        )
        product2 = product_factory.create(
            owner=seller_user2,
            title="user1_product_2",
            description="expensive",
            price=25999,
            available_stock={"default": 7},
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
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )
        assert response.status_code == 400
        assert response.json() == {
            "error": f"available stock for product {product1.id} is less than desired amount"
        }

        # verify no order was made
        assert (
            Order.objects.filter(customer=buyer)
            .filter(products__in=[product1.id, product2.id])
            .count()
            == 0
        )

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
        default_user: User,
        default_user_long_lived_access_token: AccessToken,
    ):
        non_existing_product_id1 = uuid.uuid4()
        non_existing_product_id2 = uuid.uuid4()
        buyer = default_user

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
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )
        assert response.status_code == 400
        assert response.json().keys() == set(["error", "detail"])
        assert (
            response.json()["error"]
            == "requested products and/or stock variants that do not exist"
        )

        expected_errors = [
            [str(non_existing_product_id1), "default"],
            [str(non_existing_product_id2), "default"],
        ]
        assert len(response.json()["detail"]) == len(expected_errors)
        for err in expected_errors:
            assert err in response.json()["detail"]

        # verify no order was made
        assert (
            Order.objects.filter(customer=buyer)
            .filter(products__in=[non_existing_product_id1, non_existing_product_id2])
            .count()
            == 0
        )

    def test_attempting_to_create_orders_for_non_existing_products_variants_results_in_error(
        self,
        api_client: Client,
        default_user: User,
        default_user_long_lived_access_token: AccessToken,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        seller_user = user_factory.create("user1@user1.com", "user1", "somePasswd")
        buyer = default_user

        product = product_factory.create(
            owner=seller_user,
            title="very nice t-shirt",
            description="colourful t-shirt",
            price=2500,
            available_stock={"default": 7},
        )

        response = api_client.post(
            "http://testserver/api/orders/",
            content_type="application/json",
            data={
                "products": [
                    {
                        "id": str(product.id),
                        "variant": "XXXXXXXL",
                        "quantity": 1,
                    },
                ]
            },
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )
        assert response.status_code == 400
        assert response.json() == {
            "error": "requested products and/or stock variants that do not exist",
            "detail": [[str(product.id), "XXXXXXXL"]],
        }

        # verify no order was made
        assert (
            Order.objects.filter(customer=buyer)
            .filter(products__in=[product.id])
            .count()
            == 0
        )

    def test_attempting_to_create_order_for_deleted_product_results_in_error(
        self,
        api_client: Client,
        default_user: User,
        default_user_long_lived_access_token: AccessToken,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        seller_user = user_factory.create("user1@user1.com", "user1", "somePasswd")
        buyer = default_user

        product = product_factory.create(
            deleted=timezone.now(),
            owner=seller_user,
            title="very nice t-shirt",
            description="colourful t-shirt",
            price=2500,
            available_stock={"default": 7},
        )

        response = api_client.post(
            "http://testserver/api/orders/",
            content_type="application/json",
            data={
                "products": [
                    {
                        "id": str(product.id),
                        "variant": "default",
                        "quantity": 1,
                    },
                ]
            },
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )
        assert response.status_code == 400
        assert response.json() == {
            "error": "requested products and/or stock variants that do not exist",
            "detail": [[str(product.id), "default"]],
        }

        # verify no order was made
        assert (
            Order.objects.filter(customer=buyer)
            .filter(products__in=[product.id])
            .count()
            == 0
        )

    def test_orders_can_have_multiple_variants_of_the_same_product(
        self,
        api_client: Client,
        default_user: User,
        default_user_long_lived_access_token: AccessToken,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        seller_user = user_factory.create("user1@user1.com", "user1", "easyPass")
        buyer_user = default_user

        product = product_factory.create(
            owner=seller_user,
            title="t-shirt",
            description="cheap and amazing t-shirts",
            price=1003,
            available_stock={"x": 2, "m": 5, "s": 3, "ss": 1},
        )

        request_payload = {
            "products": [
                {"id": str(product.id), "variant": "x", "quantity": 1},
                {"id": str(product.id), "variant": "m", "quantity": 2},
                {"id": str(product.id), "variant": "ss", "quantity": 1},
            ]
        }

        response = api_client.post(
            "http://testserver/api/orders/",
            content_type="application/json",
            data=request_payload,
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
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
            OrderLineItem(order=order, product=product, variant="x", quantity=1),
            OrderLineItem(order=order, product=product, variant="m", quantity=2),
            OrderLineItem(order=order, product=product, variant="ss", quantity=1),
        ]

        product.refresh_from_db()
        assert product.state == Product.STATE_AVAILABLE
        assert list(product.stock.values("product_id", "variant", "available")) == [
            {"product_id": product.id, "variant": "x", "available": 1},
            {"product_id": product.id, "variant": "m", "available": 3},
            {"product_id": product.id, "variant": "s", "available": 3},
            {"product_id": product.id, "variant": "ss", "available": 0},
        ]

    def test_users_can_fetch_own_orders(
        self,
        api_client: Client,
        default_user: User,
        default_user_long_lived_access_token: AccessToken,
        user_factory: UserFactory,
        product_factory: ProductFactory,
        order_factory: OrderFactory,
    ):
        seller_user = user_factory.create("user1@user1.com", "user1", "easyPass")
        buyer_user = default_user

        product = product_factory.create(
            owner=seller_user,
            title="t-shirt",
            description="cheap and amazing t-shirts",
            price=1003,
            available_stock={"x": 500, "m": 500, "s": 500, "ss": 500},
        )

        # TODO add cancelled order - should they be seen by the users? check state names in order model first
        pending_order = order_factory.create(
            buyer_user, [(product, "x", 1)], state=Order.States.PENDING
        )

        confirmed_order = order_factory.create(
            buyer_user, [(product, "m", 2)], state=Order.States.CONFIRMED
        )

        paid_order = order_factory.create(
            buyer_user, [(product, "s", 2)], state=Order.States.PAID
        )

        shipped_order = order_factory.create(
            buyer_user, [(product, "ss", 1)], state=Order.States.SHIPPED
        )

        response = api_client.get(
            "http://testserver/api/orders/",
            content_type="application/json",
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )
        assert response.status_code == 200

        assert response.json() == [
            {
                "id": str(pending_order.id),
                "state": "PENDING",
                "order_line_items": [
                    {
                        "product_id": str(product.id),
                        "quantity": 1,
                        "variant": "x",
                    }
                ],
            },
            {
                "id": str(confirmed_order.id),
                "state": "CONFIRMED",
                "order_line_items": [
                    {
                        "product_id": str(product.id),
                        "quantity": 2,
                        "variant": "m",
                    }
                ],
            },
            {
                "id": str(paid_order.id),
                "state": "PAID",
                "order_line_items": [
                    {
                        "product_id": str(product.id),
                        "quantity": 2,
                        "variant": "s",
                    }
                ],
            },
            {
                "id": str(shipped_order.id),
                "state": "SHIPPED",
                "order_line_items": [
                    {
                        "product_id": str(product.id),
                        "quantity": 1,
                        "variant": "ss",
                    }
                ],
            },
        ]

    def test_orders_need_to_be_confirmed_from_pending(
        self,
        api_client: Client,
        default_user: User,
        default_user_long_lived_access_token: AccessToken,
        user_factory: UserFactory,
        product_factory: ProductFactory,
        order_factory: OrderFactory,
    ):
        seller_user = user_factory.create("user1@user1.com", "user1", "easyPass")
        buyer_user = default_user

        product = product_factory.create(
            owner=seller_user,
            title="t-shirt",
            description="cheap and amazing t-shirts",
            price=1003,
            available_stock={"x": 500, "m": 500, "s": 500, "ss": 500},
        )

        pending_order = order_factory.create(
            buyer_user, [(product, "m", 1)], state=Order.States.PENDING
        )

        response = api_client.post(
            f"http://testserver/api/orders/{pending_order.id}/confirm/",
            content_type="application/json",
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            "id": str(pending_order.id),
            "state": "CONFIRMED",
            "order_line_items": [
                {
                    "product_id": str(product.id),
                    "quantity": 1,
                    "variant": "m",
                }
            ],
        }

    def test_confirming_orders_that_do_not_exist_results_in_not_found_error(
        self,
        api_client: Client,
        default_user_long_lived_access_token: AccessToken,
    ):
        response = api_client.post(
            f"http://testserver/api/orders/{uuid.uuid4()}/confirm/",
            content_type="application/json",
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )
        assert response.status_code == 404

    def test_confirming_a_confirmed_order_is_a_NOOP(
        self,
        api_client: Client,
        default_user: User,
        default_user_long_lived_access_token: AccessToken,
        user_factory: UserFactory,
        product_factory: ProductFactory,
        order_factory: OrderFactory,
    ):
        seller_user = user_factory.create("user1@user1.com", "user1", "easyPass")
        buyer_user = default_user

        product = product_factory.create(
            owner=seller_user,
            title="t-shirt",
            description="cheap and amazing t-shirts",
            price=1003,
            available_stock={"x": 500, "m": 500, "s": 500, "ss": 500},
        )

        order = order_factory.create(
            buyer_user, [(product, "s", 2)], state=Order.States.CONFIRMED
        )
        original_update_time = order.updated

        response = api_client.post(
            f"http://testserver/api/orders/{order.id}/confirm/",
            content_type="application/json",
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            "id": str(order.id),
            "state": "CONFIRMED",
            "order_line_items": [
                {
                    "product_id": str(product.id),
                    "quantity": 2,
                    "variant": "s",
                }
            ],
        }
        order.refresh_from_db()
        assert order.updated == original_update_time

    @pytest.mark.parametrize(
        "original_state",
        [
            Order.States.CANCELLED,
            Order.States.PAID,
            Order.States.REVERTED,
            Order.States.SHIPPED,
        ],
    )
    def test_confirming_orders_which_are_not_pending_or_confirmed_is_a_bad_request(
        self,
        original_state: str,
        api_client: Client,
        default_user: User,
        default_user_long_lived_access_token: AccessToken,
        user_factory: UserFactory,
        product_factory: ProductFactory,
        order_factory: OrderFactory,
    ):
        seller_user = user_factory.create("user1@user1.com", "user1", "easyPass")
        buyer_user = default_user

        product = product_factory.create(
            owner=seller_user,
            title="t-shirt",
            description="cheap and amazing t-shirts",
            price=1003,
            available_stock={"x": 500, "m": 500, "s": 500, "ss": 500},
        )

        order = order_factory.create(
            buyer_user, [(product, "s", 2)], state=original_state
        )
        original_update_time = order.updated

        response = api_client.post(
            f"http://testserver/api/orders/{order.id}/confirm/",
            content_type="application/json",
            headers={
                "Authorization": f"Bearer {default_user_long_lived_access_token.token}"
            },
        )
        assert response.status_code == 400
        order.refresh_from_db()
        assert order.updated == original_update_time
