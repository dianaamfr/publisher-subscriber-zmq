from __future__ import annotations

import json
import os

from .state import State


class SubscriberState(State):
    # --------------------------------------------------------------------------
    # Initialization
    # --------------------------------------------------------------------------

    topics: list  # subscribed topics
    messages_received: dict  # messages_received[topic] = message_id
    last_get: str | None  # last topic that was requested with GET

    def __init__(self, data_path: str, topics_json: str) -> None:
        super().__init__(data_path)
        self.topics = self.get_topics(topics_json)
        self.messages_received = {}
        self.last_get = None

    def get_topics(self, topics_json: str):
        f = open(topics_json + ".json")
        topics = json.load(f).get("topics")
        f.close()
        return topics

    def is_new_subscriber(self, data_path: str):
        return not os.path.isfile(data_path)

    def add_message(self, topic: str, msg_id: int):
        self.messages_received[topic] = msg_id

    def get_next_message(self, topic: str):
        if self.messages_received.get(topic) is None:
            return 0
        return self.messages_received[topic] + 1

    def get_last_ack(self):
        if self.last_get is None:
            return None

        msg_id = self.messages_received.get(self.last_get)
        if msg_id is None:
            return None

        return ["ACK", self.last_get, msg_id]

    def set_last_get(self, topic: str):
        self.last_get = topic

    @staticmethod
    def read_state(data_path: str, topics_json: str):
        state = State.get_state_from_file(data_path)
        if state is None:
            return SubscriberState(data_path, topics_json)
        return state

    def __str__(self):
        str_topics = json.dumps(self.topics)
        str_messages_received = json.dumps(self.messages_received)
        str_last_get = json.dumps(self.last_get)

        return f""""
            [TOPICS] subscribed topics
            {str_topics}

            [MESSAGES_RECEIVED] messages_received[<topic>] = message_id
            {str_messages_received}

            [LAST_GET] last topic that was requested with GET
            {str_last_get}
        """

    def delete(self):
        if os.path.exists(self.data_path):
            os.remove(self.data_path)
            print("=== State deleted ===")
