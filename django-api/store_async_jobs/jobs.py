from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BlockingScheduler
from django.db import transaction

from store_api.models import Order


def cancel_elapsed_unconfirmed_orders(confirmation_max_duration_seconds: int):
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


# TODO to be started by a separate process
def start(confirmation_max_duration_seconds: int, interval_seconds: int):
    scheduler = BlockingScheduler()
    scheduler.add_job(
        cancel_elapsed_unconfirmed_orders,
        args=[confirmation_max_duration_seconds],
        trigger="interval",
        seconds=interval_seconds,
        coalesce=True,
        max_instances=1,
    )

    scheduler.start()
