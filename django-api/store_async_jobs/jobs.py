import argparse
import logging
import os
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BlockingScheduler
from django.db import transaction


def cancel_elapsed_unconfirmed_orders(confirmation_max_duration_seconds: int):
    # this allows django to be configured first, before loading the models module which requires such config
    from store_api.models import Order

    logging.debug("Querying for orders to be cancelled...")
    now_utc = datetime.now(timezone.utc)
    to_confirm_threshold_time = now_utc - timedelta(
        seconds=confirmation_max_duration_seconds + 1
    )
    orders_to_cancel = (
        Order.objects.prefetch_related("orderlineitem_set")
        .filter(state=Order.States.PENDING)
        .filter(created__lte=to_confirm_threshold_time)
        .select_for_update()
    )

    with transaction.atomic():
        for order in orders_to_cancel:
            order.revert()
            order.save()
            logging.info(f"cancelled order {order.id}")


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

    logging.debug("starting scheduler...")
    print("starting!!!")
    scheduler.start()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        prog="store background jobs",
        description="Application that runs store background jobs",
    )
    argparser.add_argument(
        "-l",
        "--log-level",
        choices=[
            logging.getLevelName(logging.ERROR),
            logging.getLevelName(logging.WARN),
            logging.getLevelName(logging.INFO),
            logging.getLevelName(logging.DEBUG),
        ],
        default=logging.INFO,
    )

    args = argparser.parse_args()
    logging.root.setLevel(args.log_level)

    confirmation_max_duration_seconds = os.getenv(
        "JOB_ORDER_CANCEL_PENDING_ORDERS_TIME_SECONDS", 30
    )
    interval_seconds = os.getenv("JOB_ORDER_CANCEL_PENDING_ORDERS_INTERVAL_SECONDS", 5)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_api.settings")
    import django

    django.setup()

    start(confirmation_max_duration_seconds, interval_seconds)
