import threading


class Topic:
    """An append-only log. Subscribers read it by offset; nothing is ever removed."""

    def __init__(self, name):
        self.name = name
        self._messages = []
        self._condition = threading.Condition()
        self._closed = False

    def publish(self, message):
        with self._condition:
            self._messages.append(message)
            self._condition.notify_all()

    def message_at(self, offset):
        """Block until a message exists at offset. Returns None once the topic closes."""
        with self._condition:
            while offset >= len(self._messages) and not self._closed:
                self._condition.wait()
            return None if offset >= len(self._messages) else self._messages[offset]

    def size(self):
        with self._condition:
            return len(self._messages)

    def close(self):
        with self._condition:
            self._closed = True
            self._condition.notify_all()
