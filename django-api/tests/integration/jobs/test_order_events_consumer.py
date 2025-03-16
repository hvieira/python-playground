import uuid

import pytest

from store_api.models import Order, User
from store_async_jobs.consumer import DebeziumRedisEvent
from store_async_jobs.order_events_consumer import OrderEventConsumer
from tests.conftest import OrderFactory, ProductFactory, UserFactory


@pytest.mark.django_db()
class TestCancelNonConfirmedOrders:

    def test_process_event_new_pending_order_is_a_NOOP(
        self,
        default_user: User,
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
            buyer_user, [(product, "s", 2)], state=Order.States.PENDING
        )

        redis_event_id = "1740218269024-0"

        event = DebeziumRedisEvent(
            id=redis_event_id,
            before=None,
            after={
                "id": "ef9b5beb-9c21-4d66-a769-47207c205bbe",
                "created": "2025-02-22T09:57:48.517360Z",
                "updated": "2025-02-22T09:57:48.517831Z",
                "deleted": None,
                "state": "PENDING",
                "customer_id": "7a000c94-6dcb-4d66-bb4f-58b61d2c5dcb",
            },
        )

        consumer = OrderEventConsumer(None, None, None, None)

        event_id = consumer.process_change_event(event)

        assert event_id == redis_event_id

        order.refresh_from_db()
        assert order.state == Order.States.PENDING

    def test_process_event_order_is_confirmed(
        self,
        default_user: User,
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

        redis_event_id = "1740218269024-0"

        event = DebeziumRedisEvent(
            id=redis_event_id,
            before={
                "id": str(order.id),
                "created": "2025-02-22T09:57:48.517360Z",
                "updated": "2025-02-22T09:57:48.517831Z",
                "deleted": None,
                "state": "PENDING",
                "customer_id": "7a000c94-6dcb-4d66-bb4f-58b61d2c5dcb",
            },
            after={
                "id": str(order.id),
                "created": "2025-02-22T09:57:48.517360Z",
                "updated": "2025-02-22T09:57:51.510003Z",
                "deleted": None,
                "state": "CONFIRMED",
                "customer_id": "7a000c94-6dcb-4d66-bb4f-58b61d2c5dcb",
            },
        )

        consumer = OrderEventConsumer(None, None, None, None)

        event_id = consumer.process_change_event(event)

        assert event_id == redis_event_id

        order.refresh_from_db()
        assert order.state == Order.States.PAID

    def test_events_related_to_non_existing_orders_are_NOOP(
        self,
    ):
        non_existing_order_id = uuid.uuid4()

        redis_event_id = "1740218269024-0"

        event = DebeziumRedisEvent(
            id=redis_event_id,
            before={
                "id": str(non_existing_order_id),
                "created": "2025-02-22T09:57:48.517360Z",
                "updated": "2025-02-22T09:57:48.517831Z",
                "deleted": None,
                "state": "PENDING",
                "customer_id": "7a000c94-6dcb-4d66-bb4f-58b61d2c5dcb",
            },
            after={
                "id": str(non_existing_order_id),
                "created": "2025-02-22T09:57:48.517360Z",
                "updated": "2025-02-22T09:57:51.510003Z",
                "deleted": None,
                "state": "CONFIRMED",
                "customer_id": "7a000c94-6dcb-4d66-bb4f-58b61d2c5dcb",
            },
        )

        consumer = OrderEventConsumer(None, None, None, None)

        event_id = consumer.process_change_event(event)

        assert event_id == redis_event_id

        assert Order.objects.filter(id=non_existing_order_id).count() == 0
