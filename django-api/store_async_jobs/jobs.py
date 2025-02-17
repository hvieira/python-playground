import logging
import os
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BlockingScheduler
from django.db import transaction

LOGGER = logging.getLogger(__name__)


def cancel_elapsed_unconfirmed_orders(confirmation_max_duration_seconds: int):
    # this allows django to be configured first, before loading the models module which requires such config
    from store_api.models import Order

    LOGGER.debug("Querying for orders to be cancelled...")
    now_utc = datetime.now(timezone.utc)
    elasped_time = now_utc - timedelta(seconds=confirmation_max_duration_seconds)
    orders_to_cancel = (
        Order.objects.filter(state=Order.States.PENDING)
        .filter(created__gt=elasped_time)
        .select_for_update()
    )

    with transaction.atomic():
        for order in orders_to_cancel:
            order.cancel()
            order.save()
            LOGGER.info(f"cancelled order {order.id}")


def start(confirmation_max_duration_seconds: int, interval_seconds: int):
    scheduler = BlockingScheduler()
    scheduler.add_job(
        cancel_elapsed_unconfirmed_orders,
        args=[confirmation_max_duration_seconds],
        trigger="interval",
        seconds=interval_seconds,
        coalesce=True,
        max_instances=1,
        next_run_time=datetime.now(timezone.utc),
    )

    scheduler.start()


if __name__ == "__main__":

    confirmation_max_duration_seconds = os.getenv(
        "JOB_ORDER_CANCEL_PENDING_ORDERS_TIME_SECONDS", 30
    )
    interval_seconds = os.getenv("JOB_ORDER_CANCEL_PENDING_ORDERS_INTERVAL_SECONDS", 5)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_api.settings")

    import django

    django.setup()

    start(confirmation_max_duration_seconds, interval_seconds)
