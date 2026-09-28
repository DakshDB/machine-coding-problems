import threading
import time

from core.subscription import Subscription
from models.topic import Topic


class Broker:
    """Owns the topics and wires consumers to them."""

    def __init__(self):
        self._lock = threading.Lock()
        self._topics = {}
        self._subscriptions = {}          # (topic_name, consumer_id) -> Subscription

    def create_topic(self, name):
        with self._lock:
            return self._topics.setdefault(name, Topic(name))

    def publish(self, topic_name, message):
        self._topic(topic_name).publish(message)

    def subscribe(self, topic_name, consumer):
        topic = self._topic(topic_name)
        with self._lock:
            key = (topic_name, consumer.id)
            if key in self._subscriptions:
                return
            self._subscriptions[key] = Subscription(topic, consumer)
            self._subscriptions[key].start()

    def wait_for_drain(self, timeout=2.0):
        """Block until every subscription has delivered everything published so far."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with self._lock:
                subscriptions = list(self._subscriptions.values())
            if all(s.caught_up() for s in subscriptions):
                return True
            time.sleep(0.005)
        return False

    def shutdown(self):
        with self._lock:
            topics = list(self._topics.values())
            subscriptions = list(self._subscriptions.values())
        for topic in topics:
            topic.close()
        for subscription in subscriptions:
            subscription.join(timeout=1.0)

    def _topic(self, name):
        with self._lock:
            topic = self._topics.get(name)
        if topic is None:
            raise KeyError(f"unknown topic '{name}'")
        return topic
