from pathlib import Path
from os import linesep
from common import EVENT_SEPARATOR


def emit(event: str, topic: str, data_store_base_path='.'):
    topic_path = Path(data_store_base_path) / topic
    
    with topic_path.open('at') as topic_store_file:
        topic_store_file.write(event + linesep)

def emit_bytes(event: str, topic: str, data_store_base_path='.'):
    topic_path = Path(data_store_base_path) / topic
    
    with topic_path.open('at') as topic_store_file:
        topic_store_file.write(event + EVENT_SEPARATOR)


emit_bytes('{"payload": "dummy"}', 'test_topic')