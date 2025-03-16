# import redis
import json
import logging
from dataclasses import dataclass

from redis import Redis
from redis.exceptions import ResponseError


@dataclass
class RedisStreamEvent:
    id: str
    payload: dict


@dataclass
class DebeziumRedisEvent:
    id: str
    before: dict
    after: dict

    @staticmethod
    def from_redis_stream_event(event: RedisStreamEvent):
        raw_json = list(event.payload.values())[0]
        json_data = json.loads(raw_json)

        return DebeziumRedisEvent(
            id=event.id,
            before=json_data["payload"]["before"],
            after=json_data["payload"]["after"],
        )


class Consumer:
    def __init__(
        self,
        redis_host_name: str,
        stream_name: str,
        consumer_group_name: str,
        consumer_name: str,
        logger: logging.Logger = None,
        last_id: str = "$",
    ):
        self.redis_host_name = redis_host_name
        self.stream_name = stream_name
        self.consumer_group_name = consumer_group_name
        self.consumer_name = consumer_name
        self.last_id = last_id

        self.redis_connection: Redis = None
        if logger is None:
            self.logger: logging.Logger = logging.getLogger(
                f"{consumer_group_name}-{consumer_name}"
            )
            self.logger.setLevel(logging.INFO)
        else:
            self.logger = logger

    def init(self):
        self.redis_connection = Redis(
            self.redis_host_name, protocol=3, decode_responses=True
        )
        try:
            reply = self.redis_connection.xgroup_create(
                self.stream_name, self.consumer_group_name, self.last_id, mkstream=True
            )
            self.logger.info(f"reply when creating consumer group - {reply}")
        except ResponseError as e:
            if e.args[0] != "BUSYGROUP Consumer Group name already exists":
                self.logger.error("Failed to start consumer")
                raise e

    def read_events(self, event_count: int = 10) -> list[RedisStreamEvent]:
        # TODO read https://redis.io/docs/latest/develop/data-types/streams/ and understand how to deal with pending messages, claim and autoclaim

        # see pending messages first
        pending_messages_response = self.redis_connection.xreadgroup(
            groupname=self.consumer_group_name,
            consumername=self.consumer_name,
            streams={self.stream_name: "0"},
        )

        events_to_process = []
        if (
            self.stream_name in pending_messages_response
            and len(pending_messages_response[self.stream_name][0]) > 0
        ):
            # TODO understand why it returns a list with just a single element. Is this related to the protocol 3?
            # TODO this is duplicated. TDD and improve upon it
            for raw_event in pending_messages_response[self.stream_name][0]:
                event = RedisStreamEvent(raw_event[0], raw_event[1])
                events_to_process.append(event)

        else:
            response = self.redis_connection.xreadgroup(
                groupname=self.consumer_group_name,
                consumername=self.consumer_name,
                count=event_count,
                streams={self.stream_name: ">"},
            )
            # TODO this is duplicated. TDD and improve upon it
            for raw_event in response[self.stream_name][0]:
                event = RedisStreamEvent(raw_event[0], raw_event[1])
                events_to_process.append(event)

        return events_to_process

    def confirm_event_processed(self, event_id: str):
        # TODO sends an XACK command to redis to confirm event was processed for the specified consumer group
        pass

    def process_events(self):
        events = self.read_events()
        for event in events:
            event_id = self.process_event(event)
            self.confirm_event_processed(event_id)

    def process_event(self, event: RedisStreamEvent) -> str:
        raise NotImplementedError


class RedisDebeziumStreamConsumer(Consumer):

    def process_event(self, event: RedisStreamEvent) -> str:
        debezium_event = DebeziumRedisEvent.from_redis_stream_event(event)
        self.process_change_event(debezium_event)

    def process_change_event(self, event: DebeziumRedisEvent):
        raise NotImplementedError
