from datetime import timedelta

import pytest
from django.utils import timezone

from store_api.models import Order, OrderLineItem, User
from store_async_jobs.jobs import cancel_elapsed_unconfirmed_orders
from tests.conftest import ProductFactory, UserFactory

TIME_TO_CANCEL_PENDING_ORDERS_SECONDS = 3


@pytest.mark.django_db()
class TestCancelNonConfirmedOrders:

    def test_unconfirmed_orders_that_have_not_elapsed_are_not_cancelled(
        self,
        default_user: User,
        user_factory: UserFactory,
        product_factory: ProductFactory,
    ):
        now = timezone.now()
        elapsed = now - timedelta(seconds=TIME_TO_CANCEL_PENDING_ORDERS_SECONDS)
        seller = user_factory.create("test@test.com", "test_seller", "Passwd")
        product = product_factory.create(seller, "some product", "description", 100)
        order = Order.objects.create(
            state=Order.States.PENDING, customer=default_user, created=elapsed
        )
        OrderLineItem.objects.create(
            order=order, product=product, variant="default", quantity=1
        )

        # TODO have other orders in another states to check that they're unafected by this behaviour

        cancel_elapsed_unconfirmed_orders(TIME_TO_CANCEL_PENDING_ORDERS_SECONDS)

        order.refresh_from_db()
        assert order.state == Order.States.CANCELLED
