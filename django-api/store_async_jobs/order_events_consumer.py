import argparse
import logging
import os
import uuid

import redis

from store_async_jobs.consumer import DebeziumRedisEvent, RedisDebeziumStreamConsumer


class OrderEventConsumer(RedisDebeziumStreamConsumer):

    def process_change_event(self, event: DebeziumRedisEvent) -> str:
        from store_api.models import Order

        before_state = event.before["state"] if event.before else None
        after_state = event.after["state"] if event.after else None

        match (before_state, after_state):
            case (Order.States.PENDING, Order.States.CONFIRMED):
                order_id = uuid.UUID(event.after["id"])
                try:
                    order = Order.objects.select_for_update().get(id=order_id)
                    order.process_payment()
                    order.save()
                except Order.DoesNotExist:
                    logging.warning(
                        "Order %s from event %s was not found. Ignoring...",
                        str(order_id),
                        event.id,
                    )

            # TODO
            # case (Order.States.PAID, Order.States.SHIPPED):
            # dummy shipping process

            case _:
                # TODO if this is a NOOP, the event should be ack'ed to remove it from the pending message list
                pass

        return event.id


def start():
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

    # start process
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_api.settings")
    import django

    django.setup()

    redis_host = os.environ["REDIS_HOST"]
    redis_client = redis.Redis(redis_host, decode_responses=True, protocol=3)

    consumer = OrderEventConsumer(
        redis_client=redis_client,
        stream_name="store.public.store_api_order",
        consumer_group_name="store_consumer_order",
        # this would be based on HOST or POD NAME or something else to be unique
        consumer_name="order-consumer",
        # process all messages from the stream, not just new ones
        consumer_group_start_id="0",
    )
    consumer.init()

    while True:
        consumer.process_events()


if __name__ == "__main__":
    start()
