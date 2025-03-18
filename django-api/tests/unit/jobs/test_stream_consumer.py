# event = RedisStreamEvent(
#     id=redis_event_id,
#     payload={'{"schema":{"type":"struct","fields":[{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"id"}],"optional":false,"name":"store.public.store_api_order.Key"},"payload":{"id":"ef9b5beb-9c21-4d66-a769-47207c205bbe"}}': '{"schema":{"type":"struct","fields":[{"type":"struct","fields":[{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"id"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"created"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"updated"},{"type":"string","optional":true,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"deleted"},{"type":"string","optional":false,"field":"state"},{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"customer_id"}],"optional":true,"name":"store.public.store_api_order.Value","field":"before"},{"type":"struct","fields":[{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"id"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"created"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"updated"},{"type":"string","optional":true,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"deleted"},{"type":"string","optional":false,"field":"state"},{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"customer_id"}],"optional":true,"name":"store.public.store_api_order.Value","field":"after"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"version"},{"type":"string","optional":false,"field":"connector"},{"type":"string","optional":false,"field":"name"},{"type":"int64","optional":false,"field":"ts_ms"},{"type":"string","optional":true,"name":"io.debezium.data.Enum","version":1,"parameters":{"allowed":"true,last,false,incremental"},"default":"false","field":"snapshot"},{"type":"string","optional":false,"field":"db"},{"type":"string","optional":true,"field":"sequence"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"},{"type":"string","optional":false,"field":"schema"},{"type":"string","optional":false,"field":"table"},{"type":"int64","optional":true,"field":"txId"},{"type":"int64","optional":true,"field":"lsn"},{"type":"int64","optional":true,"field":"xmin"}],"optional":false,"name":"io.debezium.connector.postgresql.Source","field":"source"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"id"},{"type":"int64","optional":false,"field":"total_order"},{"type":"int64","optional":false,"field":"data_collection_order"}],"optional":true,"name":"event.block","version":1,"field":"transaction"},{"type":"string","optional":false,"field":"op"},{"type":"int64","optional":true,"field":"ts_ms"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"}],"optional":false,"name":"store.public.store_api_order.Envelope","version":2},"payload":{"before":null,"after":{"id":"ef9b5beb-9c21-4d66-a769-47207c205bbe","created":"2025-02-22T09:57:48.517360Z","updated":"2025-02-22T09:57:48.517831Z","deleted":null,"state":"PENDING","customer_id":"7a000c94-6dcb-4d66-bb4f-58b61d2c5dcb"},"source":{"version":"3.0.0.Final","connector":"postgresql","name":"store","ts_ms":1740218268541,"snapshot":"false","db":"store","sequence":"[\\"2078959952\\",\\"2078978480\\"]","ts_us":1740218268541456,"ts_ns":1740218268541456000,"schema":"public","table":"store_api_order","txId":32545,"lsn":2078978480,"xmin":null},"transaction":null,"op":"c","ts_ms":1740218269005,"ts_us":1740218269005541,"ts_ns":1740218269005541665}}'})

from unittest.mock import Mock, call

import pytest
from redis import Redis

from store_async_jobs.consumer import Consumer, RedisStreamEvent


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

    def test_consumer_init_handles_consumer_group_setup(self, redis_client):
        redis_client.xgroup_create = Mock(return_value="OK")

        consumer = Consumer(
            redis_client,
            self.DUMMY_REDIS_STREAM_NAME,
            self.DUMMY_REDIS_STREAM_CONSUMER_GROUP_NAME,
            self.DUMMY_REDIS_CONSUMER_NAME,
        )
        consumer.init()

        redis_client.xgroup_create.assert_called_once_with(
            self.DUMMY_REDIS_STREAM_NAME,
            self.DUMMY_REDIS_STREAM_CONSUMER_GROUP_NAME,
            "$",
            mkstream=True,
        )

    def test_consumer_init_handles_consumer_group_already_created(self, redis_client):
        redis_client.xgroup_create = Mock(
            return_value="BUSYGROUP Consumer Group name already exists"
        )

        consumer = Consumer(
            redis_client,
            self.DUMMY_REDIS_STREAM_NAME,
            self.DUMMY_REDIS_STREAM_CONSUMER_GROUP_NAME,
            self.DUMMY_REDIS_CONSUMER_NAME,
        )
        consumer.init()

        redis_client.xgroup_create.assert_called_once_with(
            self.DUMMY_REDIS_STREAM_NAME,
            self.DUMMY_REDIS_STREAM_CONSUMER_GROUP_NAME,
            "$",
            mkstream=True,
        )

    def test_consumer_reads_from_stream_checks_idle_pending_messages_then_its_pending_messages_then_new_messages(
        self, redis_client
    ):
        mock_order_manager = Mock()
        xautoclaim_mock = Mock(return_value=["0-0", [], []])
        redis_client.xautoclaim = xautoclaim_mock
        mock_order_manager.attach_mock(xautoclaim_mock, "xautoclaim")

        xreadgroup_mock = Mock(return_value={})
        redis_client.xreadgroup = xreadgroup_mock
        mock_order_manager.attach_mock(xreadgroup_mock, "xreadgroup")

        consumer = Consumer(
            redis_client,
            self.DUMMY_REDIS_STREAM_NAME,
            self.DUMMY_REDIS_STREAM_CONSUMER_GROUP_NAME,
            self.DUMMY_REDIS_CONSUMER_NAME,
        )
        events = consumer.read_events()

        assert events == []
        assert len(mock_order_manager.mock_calls) > 0
        assert mock_order_manager.mock_calls == [
            call.xautoclaim(
                self.DUMMY_REDIS_STREAM_NAME,
                self.DUMMY_REDIS_STREAM_CONSUMER_GROUP_NAME,
                self.DUMMY_REDIS_CONSUMER_NAME,
                60 * 1000,
                count=10,
            ),
            call.xreadgroup(
                groupname=self.DUMMY_REDIS_STREAM_CONSUMER_GROUP_NAME,
                consumername=self.DUMMY_REDIS_CONSUMER_NAME,
                count=10,
                streams={self.DUMMY_REDIS_STREAM_NAME: "0-0"},
            ),
            call.xreadgroup(
                groupname=self.DUMMY_REDIS_STREAM_CONSUMER_GROUP_NAME,
                consumername=self.DUMMY_REDIS_CONSUMER_NAME,
                count=10,
                streams={self.DUMMY_REDIS_STREAM_NAME: ">"},
            ),
        ]

    def test_consumer_prioritizes_idle_pending_messages_if_there_are_any(
        self, redis_client
    ):
        mock_order_manager = Mock()
        xautoclaim_mock = Mock(
            return_value=[
                "1740218269024-0",
                [
                    (
                        "1740218269024-0",
                        {
                            '{"schema":{"type":"struct","fields":[{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"id"}],"optional":false,"name":"store.public.store_api_order.Key"},"payload":{"id":"ef9b5beb-9c21-4d66-a769-47207c205bbe"}}': '{"schema":{"type":"struct","fields":[{"type":"struct","fields":[{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"id"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"created"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"updated"},{"type":"string","optional":true,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"deleted"},{"type":"string","optional":false,"field":"state"},{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"customer_id"}],"optional":true,"name":"store.public.store_api_order.Value","field":"before"},{"type":"struct","fields":[{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"id"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"created"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"updated"},{"type":"string","optional":true,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"deleted"},{"type":"string","optional":false,"field":"state"},{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"customer_id"}],"optional":true,"name":"store.public.store_api_order.Value","field":"after"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"version"},{"type":"string","optional":false,"field":"connector"},{"type":"string","optional":false,"field":"name"},{"type":"int64","optional":false,"field":"ts_ms"},{"type":"string","optional":true,"name":"io.debezium.data.Enum","version":1,"parameters":{"allowed":"true,last,false,incremental"},"default":"false","field":"snapshot"},{"type":"string","optional":false,"field":"db"},{"type":"string","optional":true,"field":"sequence"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"},{"type":"string","optional":false,"field":"schema"},{"type":"string","optional":false,"field":"table"},{"type":"int64","optional":true,"field":"txId"},{"type":"int64","optional":true,"field":"lsn"},{"type":"int64","optional":true,"field":"xmin"}],"optional":false,"name":"io.debezium.connector.postgresql.Source","field":"source"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"id"},{"type":"int64","optional":false,"field":"total_order"},{"type":"int64","optional":false,"field":"data_collection_order"}],"optional":true,"name":"event.block","version":1,"field":"transaction"},{"type":"string","optional":false,"field":"op"},{"type":"int64","optional":true,"field":"ts_ms"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"}],"optional":false,"name":"store.public.store_api_order.Envelope","version":2},"payload":{"before":null,"after":{"id":"ef9b5beb-9c21-4d66-a769-47207c205bbe","created":"2025-02-22T09:57:48.517360Z","updated":"2025-02-22T09:57:48.517831Z","deleted":null,"state":"PENDING","customer_id":"7a000c94-6dcb-4d66-bb4f-58b61d2c5dcb"},"source":{"version":"3.0.0.Final","connector":"postgresql","name":"store","ts_ms":1740218268541,"snapshot":"false","db":"store","sequence":"[\\"2078959952\\",\\"2078978480\\"]","ts_us":1740218268541456,"ts_ns":1740218268541456000,"schema":"public","table":"store_api_order","txId":32545,"lsn":2078978480,"xmin":null},"transaction":null,"op":"c","ts_ms":1740218269005,"ts_us":1740218269005541,"ts_ns":1740218269005541665}}'
                        },
                    )
                ],
                [],
            ]
        )
        redis_client.xautoclaim = xautoclaim_mock
        mock_order_manager.attach_mock(xautoclaim_mock, "xautoclaim")

        xreadgroup_mock = Mock(return_value={})
        redis_client.xreadgroup = xreadgroup_mock
        mock_order_manager.attach_mock(xreadgroup_mock, "xreadgroup")

        consumer = Consumer(
            redis_client,
            self.DUMMY_REDIS_STREAM_NAME,
            self.DUMMY_REDIS_STREAM_CONSUMER_GROUP_NAME,
            self.DUMMY_REDIS_CONSUMER_NAME,
        )
        events = consumer.read_events()

        assert events == [
            RedisStreamEvent(
                id="1740218269024-0",
                payload={
                    '{"schema":{"type":"struct","fields":[{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"id"}],"optional":false,"name":"store.public.store_api_order.Key"},"payload":{"id":"ef9b5beb-9c21-4d66-a769-47207c205bbe"}}': '{"schema":{"type":"struct","fields":[{"type":"struct","fields":[{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"id"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"created"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"updated"},{"type":"string","optional":true,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"deleted"},{"type":"string","optional":false,"field":"state"},{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"customer_id"}],"optional":true,"name":"store.public.store_api_order.Value","field":"before"},{"type":"struct","fields":[{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"id"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"created"},{"type":"string","optional":false,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"updated"},{"type":"string","optional":true,"name":"io.debezium.time.ZonedTimestamp","version":1,"field":"deleted"},{"type":"string","optional":false,"field":"state"},{"type":"string","optional":false,"name":"io.debezium.data.Uuid","version":1,"field":"customer_id"}],"optional":true,"name":"store.public.store_api_order.Value","field":"after"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"version"},{"type":"string","optional":false,"field":"connector"},{"type":"string","optional":false,"field":"name"},{"type":"int64","optional":false,"field":"ts_ms"},{"type":"string","optional":true,"name":"io.debezium.data.Enum","version":1,"parameters":{"allowed":"true,last,false,incremental"},"default":"false","field":"snapshot"},{"type":"string","optional":false,"field":"db"},{"type":"string","optional":true,"field":"sequence"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"},{"type":"string","optional":false,"field":"schema"},{"type":"string","optional":false,"field":"table"},{"type":"int64","optional":true,"field":"txId"},{"type":"int64","optional":true,"field":"lsn"},{"type":"int64","optional":true,"field":"xmin"}],"optional":false,"name":"io.debezium.connector.postgresql.Source","field":"source"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"id"},{"type":"int64","optional":false,"field":"total_order"},{"type":"int64","optional":false,"field":"data_collection_order"}],"optional":true,"name":"event.block","version":1,"field":"transaction"},{"type":"string","optional":false,"field":"op"},{"type":"int64","optional":true,"field":"ts_ms"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"}],"optional":false,"name":"store.public.store_api_order.Envelope","version":2},"payload":{"before":null,"after":{"id":"ef9b5beb-9c21-4d66-a769-47207c205bbe","created":"2025-02-22T09:57:48.517360Z","updated":"2025-02-22T09:57:48.517831Z","deleted":null,"state":"PENDING","customer_id":"7a000c94-6dcb-4d66-bb4f-58b61d2c5dcb"},"source":{"version":"3.0.0.Final","connector":"postgresql","name":"store","ts_ms":1740218268541,"snapshot":"false","db":"store","sequence":"[\\"2078959952\\",\\"2078978480\\"]","ts_us":1740218268541456,"ts_ns":1740218268541456000,"schema":"public","table":"store_api_order","txId":32545,"lsn":2078978480,"xmin":null},"transaction":null,"op":"c","ts_ms":1740218269005,"ts_us":1740218269005541,"ts_ns":1740218269005541665}}'
                },
            )
        ]
        xautoclaim_mock.assert_called_once()
        xreadgroup_mock.assert_not_called()
