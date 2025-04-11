import json
import logging
from dataclasses import dataclass
from typing import Generator

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
    """
    Redis consumer for streams, based on redis clients with protocol 3 and decoded responses
    """

    def __init__(
        self,
        redis_client: Redis,
        stream_name: str,
        consumer_group_name: str,
        consumer_name: str,
        consumer_group_start_id: str = "$",
    ):
        self.redis_client = redis_client
        self.stream_name = stream_name
        self.consumer_group_name = consumer_group_name
        self.consumer_name = consumer_name
        self.consumer_group_start_id = consumer_group_start_id
        self.check_pending_messages = True

    def init(self):
        try:
            reply = self.redis_client.xgroup_create(
                self.stream_name,
                self.consumer_group_name,
                self.consumer_group_start_id,
                mkstream=True,
            )
            logging.info(f"reply when creating consumer group - {reply}")
        except ResponseError as e:
            if e.args[0] != "BUSYGROUP Consumer Group name already exists":
                logging.error("Failed to start consumer")
                raise e

    @staticmethod
    def get_event_from_redis_decoded_format(decoded_redis_stream_entry):
        return RedisStreamEvent(
            decoded_redis_stream_entry[0], decoded_redis_stream_entry[1]
        )

    def read_from_consumer_group(self, event_id_cursor: str, event_count: int):
        return self.redis_client.xreadgroup(
            groupname=self.consumer_group_name,
            consumername=self.consumer_name,
            count=event_count,
            streams={self.stream_name: event_id_cursor},
        )

    def read_events(
        self, event_count: int = 10
    ) -> Generator[RedisStreamEvent, None, None]:
        # https://redis.io/docs/latest/develop/data-types/streams/ to understand how to deal with pending messages, claim and autoclaim

        # check if there are idle messages that need to be claimed
        # this could potentially be done in a separate process
        claim_result = self.redis_client.xautoclaim(
            self.stream_name,
            self.consumer_group_name,
            self.consumer_name,
            60 * 1000,
            count=event_count,
        )

        if len(claim_result[1]) > 0:
            logging.debug("claimed idle events")
            for raw_event in claim_result[1]:
                yield Consumer.get_event_from_redis_decoded_format(raw_event)
            # focus on idle pending messages first - do not process any other messages
            return

        stream_cursor_id = "0-0" if self.check_pending_messages else ">"

        response = self.read_from_consumer_group(stream_cursor_id, event_count)
        if self.stream_name in response:
            if len(response[self.stream_name][0]) == 0:
                self.check_pending_messages = False
                return
            else:
                logging.debug(
                    f'got {"pending" if self.check_pending_messages else "new"} events'
                )
                for raw_event in response[self.stream_name][0]:
                    yield Consumer.get_event_from_redis_decoded_format(raw_event)

        else:
            self.check_pending_messages = False
            return

    def confirm_event_processed(self, event_id: str) -> None:
        self.redis_client.xack(self.stream_name, self.consumer_group_name, event_id)
        logging.info("Sucessfully processed order event with redis ID %s", event_id)

    def process_events(self):
        events = self.read_events()
        for event in events:
            logging.debug("processing event %s", event.id)
            event_id = self.process_event(event)
            self.confirm_event_processed(event_id)

    def process_event(self, event: RedisStreamEvent) -> str:
        raise NotImplementedError


class RedisDebeziumStreamConsumer(Consumer):

    def process_event(self, event: RedisStreamEvent) -> str:
        debezium_event = DebeziumRedisEvent.from_redis_stream_event(event)
        return self.process_change_event(debezium_event)

    def process_change_event(self, event: DebeziumRedisEvent) -> str:
        raise NotImplementedError
