class Producer:
    def __init__(self, producer_id, broker):
        self.id = producer_id
        self._broker = broker

    def publish(self, topic_name, message):
        self._broker.publish(topic_name, message)
