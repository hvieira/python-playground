from datetime import datetime, timedelta, timezone

import pytest

from store_api.models import Order, OrderLineItem, User
from store_async_jobs.jobs import cancel_elapsed_unconfirmed_orders
from tests.conftest import ProductFactory, UserFactory

TIME_TO_CANCEL_PENDING_ORDERS_SECONDS = 5


@pytest.mark.django_db()
class TestCancelNonConfirmedOrders:

    def test_unconfirmed_orders_that_have_not_elapsed_are_not_cancelled(
        self,
        default_user: User,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        now = datetime.now(timezone.utc)
        elapsed = now - timedelta(seconds=TIME_TO_CANCEL_PENDING_ORDERS_SECONDS)
        seller = user_factory.create("test@test.com", "test_seller", "Passwd")
        product = product_factory.create(seller, "some product", "description", 100)
        order = Order.objects.create(
            state=Order.States.PENDING, customer=default_user, created=elapsed
        )
        OrderLineItem.objects.create(
            order=order, product=product, variant="default", quantity=1
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

        order.refresh_from_db()
        assert order.state == Order.States.CANCELLED

        # confirm that other orders were not affected
        very_recent_pending_order.refresh_from_db()
        assert very_recent_pending_order.state == Order.States.PENDING

        confirmed_old_order.refresh_from_db()
        assert confirmed_old_order.state == Order.States.CONFIRMED

        paid_old_order.refresh_from_db()
        assert paid_old_order.state == Order.States.PAID

        shipped_old_order.refresh_from_db()
        assert shipped_old_order.state == Order.States.SHIPPED
