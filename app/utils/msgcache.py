from collections import deque


class MsgCache:
    def __init__(self, max_size=100):
        self.max_size = max_size
        self.cache_data = {}

    def add(self, key, value):
        if key not in self.cache_data:
            self.cache_data[key] = deque(maxlen=self.max_size)
        self.cache_data[key].append(value)

    def get(self, key):
        return self.cache_data.get(key, deque())

    def delete(self, key):
        if key in self.cache_data:
            del self.cache_data[key]

    def is_last_two_message_equal(self, qq):
        messages = self.get(qq)
        if len(messages) > 2:
            return messages[-2] == messages[-1]
