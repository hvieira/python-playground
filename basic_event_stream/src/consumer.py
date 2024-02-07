import argparse

from pathlib import Path
from common import EVENT_SEPARATOR


EMPTY_EVENT = ''


def read(topic: str, data_store_base_path='.'):
    topic_path = Path(data_store_base_path) / topic
    
    with topic_path.open('r') as topic_store_file:
        # while (line := topic_store_file.readline()) != '':
        for line in topic_store_file:
            print(line, end='')


# the start_from position needs to be either 0 (start of stream) OR an index relating to an event separator in the stream
def read_events_from_position(topic: str, start_from: int, data_store_base_path='.'):
    topic_path = Path(data_store_base_path) / topic
    
    with topic_path.open('r') as topic_store_file:
        if start_from != 0:
            topic_store_file.seek(start_from)
            char = topic_store_file.read(1)
            if char != EVENT_SEPARATOR:
                raise IndexError("start_from points to a non valid start position in the stream")
            
        while (event := _read_event(topic_store_file)) != EMPTY_EVENT:
            print(event)
                    

def _read_event(file):
    event = EMPTY_EVENT

    while (c := file.read(1)):
        if c == EVENT_SEPARATOR:
            break
        else:
            event += c

    return event


parser = argparse.ArgumentParser(description='Consumer')
parser.add_argument('--offset', type=int, default=0, required=False, help='optional offset to read from the stream')

parsed_args = parser.parse_args()

read_events_from_position('test_topic', start_from=parsed_args.offset)