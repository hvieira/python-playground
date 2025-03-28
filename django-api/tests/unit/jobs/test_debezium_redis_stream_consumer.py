from unittest.mock import Mock

import pytest
from redis import Redis

from store_async_jobs.consumer import (
    DebeziumRedisEvent,
    RedisDebeziumStreamConsumer,
    RedisStreamEvent,
)


@pytest.fixture()
def redis_hostname():
    return "localhost"


@pytest.fixture()
def redis_client(redis_hostname):
    return Redis(redis_hostname, decode_responses=True, protocol=3)


class TestRedisStreamConsumer:

    DUMMY_REDIS_STREAM_NAME = "stream_key"
    DUMMY_REDIS_STREAM_CONSUMER_GROUP_NAME = "le_consumer_group"
    DUMMY_REDIS_CONSUMER_NAME = "dummy"

    def test_consumer_process_event_transforms_event_to_expected_format_on_changes_to_new_entities(
        self, redis_client
    ):
        consumer = RedisDebeziumStreamConsumer(
            redis_client,
            self.DUMMY_REDIS_STREAM_NAME,
            self.DUMMY_REDIS_STREAM_CONSUMER_GROUP_NAME,
            self.DUMMY_REDIS_CONSUMER_NAME,
        )

        event_id = "1740218269024-0"
        consumer.process_change_event = Mock(return_value=event_id)

        returned_event_id = consumer.process_event(
            RedisStreamEvent(
                id=event_id,
                payload={
                    '{"schema":{"type":"struct","fields":[{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"id"}],"optional":false,"name":"store.public.store_api_order.Key"},"payload":{"id":"ef9b5beb-9c21-4d66-a769-47207c205bbe"}}': '{"schema":{"type":"struct","fields":[{"type":"struct","fields":[{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"id"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"created"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"updated"},{"type":"string","optional":true,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"deleted"},{"type":"string","optional":false,"field":"state"},{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"customer_id"}],"optional":true,"name":"store.public.store_api_order.Value","field":"before"},{"type":"struct","fields":[{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"id"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"created"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"updated"},{"type":"string","optional":true,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"deleted"},{"type":"string","optional":false,"field":"state"},{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"customer_id"}],"optional":true,"name":"store.public.store_api_order.Value","field":"after"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"version"},{"type":"string","optional":false,"field":"connector"},{"type":"string","optional":false,"field":"name"},{"type":"int64","optional":false,"field":"ts_ms"},{"type":"string","optional":true,"name":"io.debezium.data.Enum","version":1,"parameters":{"allowed":"true,last,false,incremental"},"default":"false","field":"snapshot"},{"type":"string","optional":false,"field":"db"},{"type":"string","optional":true,"field":"sequence"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"},{"type":"string","optional":false,"field":"schema"},{"type":"string","optional":false,"field":"table"},{"type":"int64","optional":true,"field":"txId"},{"type":"int64","optional":true,"field":"lsn"},{"type":"int64","optional":true,"field":"xmin"}],"optional":false,"name":"io.debezium.connector.postgresql.Source","field":"source"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"id"},{"type":"int64","optional":false,"field":"total_order"},{"type":"int64","optional":false,"field":"data_collection_order"}],"optional":true,"name":"event.block","version":1,"field":"transaction"},{"type":"string","optional":false,"field":"op"},{"type":"int64","optional":true,"field":"ts_ms"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"}],"optional":false,"name":"store.public.store_api_order.Envelope","version":2},"payload":{"before":null,"after":{"id":"ef9b5beb-9c21-4d66-a769-47207c205bbe","created":"2025-02-22T09:57:48.517360Z","updated":"2025-02-22T09:57:48.517831Z","deleted":null,"state":"PENDING","customer_id":"7a000c94-6dcb-4d66-bb4f-58b61d2c5dcb"},"source":{"version":"3.0.0.Final","connector":"postgresql","name":"store","ts_ms":1740218268541,"snapshot":"false","db":"store","sequence":"[\\"2078959952\\",\\"2078978480\\"]","ts_us":1740218268541456,"ts_ns":1740218268541456000,"schema":"public","table":"store_api_order","txId":32545,"lsn":2078978480,"xmin":null},"transaction":null,"op":"c","ts_ms":1740218269005,"ts_us":1740218269005541,"ts_ns":1740218269005541665}}'
                },
            )
        )

        assert returned_event_id == event_id

        consumer.process_change_event.assert_called_once_with(
            DebeziumRedisEvent(
                id=event_id,
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
        )

    def test_consumer_process_event_transforms_event_to_expected_format_on_changes_to_existing_entities(
        self, redis_client
    ):
        consumer = RedisDebeziumStreamConsumer(
            redis_client,
            self.DUMMY_REDIS_STREAM_NAME,
            self.DUMMY_REDIS_STREAM_CONSUMER_GROUP_NAME,
            self.DUMMY_REDIS_CONSUMER_NAME,
        )

        event_id = "1740218269024-0"
        consumer.process_change_event = Mock(return_value=event_id)

        returned_event_id = consumer.process_event(
            RedisStreamEvent(
                id=event_id,
                payload={
                    '{"schema":{"type":"struct","fields":[{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"id"}],"optional":false,"name":"store.public.store_api_order.Key"},"payload":{"id":"ef9b5beb-9c21-4d66-a769-47207c205bbe"}}': '{"schema":{"type":"struct","fields":[{"type":"struct","fields":[{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"id"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"created"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"updated"},{"type":"string","optional":true,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"deleted"},{"type":"string","optional":false,"field":"state"},{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"customer_id"}],"optional":true,"name":"store.public.store_api_order.Value","field":"before"},{"type":"struct","fields":[{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"id"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"created"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"updated"},{"type":"string","optional":true,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"deleted"},{"type":"string","optional":false,"field":"state"},{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"customer_id"}],"optional":true,"name":"store.public.store_api_order.Value","field":"after"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"version"},{"type":"string","optional":false,"field":"connector"},{"type":"string","optional":false,"field":"name"},{"type":"int64","optional":false,"field":"ts_ms"},{"type":"string","optional":true,"name":"io.debezium.data.Enum","version":1,"parameters":{"allowed":"true,last,false,incremental"},"default":"false","field":"snapshot"},{"type":"string","optional":false,"field":"db"},{"type":"string","optional":true,"field":"sequence"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"},{"type":"string","optional":false,"field":"schema"},{"type":"string","optional":false,"field":"table"},{"type":"int64","optional":true,"field":"txId"},{"type":"int64","optional":true,"field":"lsn"},{"type":"int64","optional":true,"field":"xmin"}],"optional":false,"name":"io.debezium.connector.postgresql.Source","field":"source"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"id"},{"type":"int64","optional":false,"field":"total_order"},{"type":"int64","optional":false,"field":"data_collection_order"}],"optional":true,"name":"event.block","version":1,"field":"transaction"},{"type":"string","optional":false,"field":"op"},{"type":"int64","optional":true,"field":"ts_ms"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"}],"optional":false,"name":"store.public.store_api_order.Envelope","version":2},"payload":{"before":{"id":"ef9b5beb-9c21-4d66-a769-47207c205bbe","created":"2025-02-22T09:57:46.517360Z","updated":"2025-02-22T09:57:47.517831Z","deleted":null,"state":"PENDING","customer_id":"7a000c94-6dcb-4d66-bb4f-58b61d2c5dcb"},"after":{"id":"ef9b5beb-9c21-4d66-a769-47207c205bbe","created":"2025-02-22T09:57:46.517360Z","updated":"2025-02-22T09:57:48.517831Z","deleted":null,"state":"CONFIRMED","customer_id":"7a000c94-6dcb-4d66-bb4f-58b61d2c5dcb"},"source":{"version":"3.0.0.Final","connector":"postgresql","name":"store","ts_ms":1740218268541,"snapshot":"false","db":"store","sequence":"[\\"2078959952\\",\\"2078978480\\"]","ts_us":1740218268541456,"ts_ns":1740218268541456000,"schema":"public","table":"store_api_order","txId":32545,"lsn":2078978480,"xmin":null},"transaction":null,"op":"c","ts_ms":1740218269005,"ts_us":1740218269005541,"ts_ns":1740218269005541665}}'
                },
            )
        )

        assert returned_event_id == event_id

        consumer.process_change_event.assert_called_once_with(
            DebeziumRedisEvent(
                id=event_id,
                before={
                    "id": "ef9b5beb-9c21-4d66-a769-47207c205bbe",
                    "created": "2025-02-22T09:57:46.517360Z",
                    "updated": "2025-02-22T09:57:47.517831Z",
                    "deleted": None,
                    "state": "PENDING",
                    "customer_id": "7a000c94-6dcb-4d66-bb4f-58b61d2c5dcb",
                },
                after={
                    "id": "ef9b5beb-9c21-4d66-a769-47207c205bbe",
                    "created": "2025-02-22T09:57:46.517360Z",
                    "updated": "2025-02-22T09:57:48.517831Z",
                    "deleted": None,
                    "state": "CONFIRMED",
                    "customer_id": "7a000c94-6dcb-4d66-bb4f-58b61d2c5dcb",
                },
            )
        )
