from datetime import datetime, timedelta, timezone

import pytest

from store_api.models import Order, OrderLineItem, User
from store_async_jobs.jobs import cancel_elapsed_unconfirmed_orders
from tests.conftest import ProductFactory, UserFactory

TIME_TO_CANCEL_PENDING_ORDERS_SECONDS = 5


@pytest.mark.django_db()
class TestCancelNonConfirmedOrders:

    def test_pending_orders_that_are_unconfirmed_over_the_time_threshold_get_cancelled(
        self,
        default_user: User,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        now = datetime.now(timezone.utc)
        elapsed = now - timedelta(seconds=TIME_TO_CANCEL_PENDING_ORDERS_SECONDS)
        seller = user_factory.create("test@test.com", "test_seller", "Passwd")
        product = product_factory.create(
            seller,
            "some product",
            "description",
            100,
            available_stock={"default": 7, "red": 11},
        )

        pending_order = Order.objects.create(
            state=Order.States.PENDING, customer=default_user, created=elapsed
        )
        OrderLineItem.objects.create(
            order=pending_order, product=product, variant="default", quantity=3
        )
        OrderLineItem.objects.create(
            order=pending_order, product=product, variant="red", quantity=4
        )

        very_recent_pending_order = Order.objects.create(
            state=Order.States.PENDING, customer=default_user, created=now
        )
        OrderLineItem.objects.create(
            order=very_recent_pending_order,
            product=product,
            variant="default",
            quantity=1,
        )

        confirmed_old_order = Order.objects.create(
            state=Order.States.CONFIRMED, customer=default_user, created=elapsed
        )
        OrderLineItem.objects.create(
            order=confirmed_old_order, product=product, variant="default", quantity=1
        )

        paid_old_order = Order.objects.create(
            state=Order.States.PAID, customer=default_user, created=elapsed
        )
        OrderLineItem.objects.create(
            order=paid_old_order, product=product, variant="default", quantity=1
        )

        shipped_old_order = Order.objects.create(
            state=Order.States.SHIPPED, customer=default_user, created=elapsed
        )
        OrderLineItem.objects.create(
            order=shipped_old_order, product=product, variant="default", quantity=1
        )

        cancel_elapsed_unconfirmed_orders(TIME_TO_CANCEL_PENDING_ORDERS_SECONDS)

        pending_order.refresh_from_db()
        assert pending_order.state == Order.States.REVERTED

        # confirm that other orders were not affected
        very_recent_pending_order.refresh_from_db()
        assert very_recent_pending_order.state == Order.States.PENDING

        confirmed_old_order.refresh_from_db()
        assert confirmed_old_order.state == Order.States.CONFIRMED

        paid_old_order.refresh_from_db()
        assert paid_old_order.state == Order.States.PAID

        shipped_old_order.refresh_from_db()
        assert shipped_old_order.state == Order.States.SHIPPED

        # confirm that quantities were restored
        product.refresh_from_db()
        assert list(
            product.stock.all().order_by("variant").values("variant", "available")
        ) == [
            {"variant": "default", "available": 10},
            {"variant": "red", "available": 15},
        ]
