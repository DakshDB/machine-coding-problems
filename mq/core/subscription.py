import threading


class Subscription(threading.Thread):
    """One consumer's cursor over one topic, advanced by its own thread."""

    def __init__(self, topic, consumer):
        super().__init__(daemon=True, name=f"{consumer.id}@{topic.name}")
        self._topic = topic
        self._consumer = consumer
        self._offset = 0

    def run(self):
        while True:
            message = self._topic.message_at(self._offset)
            if message is None:            # topic closed
                return
            self._consumer.consume(message)
            self._offset += 1              # advance only after delivery

    def caught_up(self):
        return self._offset >= self._topic.size()
