import os
import uuid

from store_api.models import Order
from store_async_jobs.consumer import DebeziumRedisEvent, RedisDebeziumStreamConsumer


class OrderEventConsumer(RedisDebeziumStreamConsumer):

    def process_change_event(self, event: DebeziumRedisEvent) -> str:
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
                    self.logger.warning(
                        "Order %s from event %s was not found. Ignoring...",
                        str(order_id),
                        event.id,
                    )

            # TODO
            # case (Order.States.PAID, Order.States.SHIPPED):
            # dummy shipping process

            case _:
                pass

        return event.id


def start():
    redis_host = os.environ["REDIS_HOST"]
    consumer = OrderEventConsumer(
        redis_host_name=redis_host,
        stream_name="store.public.store_api_order",
        consumer_group_name="store_consumer_order",
        # this would be based on HOST or POD NAME or something else to be unique
        consumer_name="order-consumer",
        # process all messages from the stream, not just new ones
        last_id="0",
    )
    consumer.init()

    while True:
        consumer.process_events()


if __name__ == "__main__":
    start()
