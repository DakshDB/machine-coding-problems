import threading
import unittest

from core.broker import Broker
from models.consumer import Consumer
from models.producer import Producer


class RecordingConsumer(Consumer):
    """Same contract, records instead of printing, so tests can assert."""

    def __init__(self, consumer_id):
        super().__init__(consumer_id)
        self.received = []
        self._lock = threading.Lock()

    def consume(self, message):
        with self._lock:
            self.received.append(message)


class TestBroker(unittest.TestCase):
    def setUp(self):
        self.broker = Broker()
        self.broker.create_topic("t")
        self.producer = Producer("p", self.broker)

    def tearDown(self):
        self.broker.shutdown()

    def test_every_consumer_gets_every_message_in_order(self):
        consumers = [RecordingConsumer(f"c{n}") for n in range(5)]
        for consumer in consumers:
            self.broker.subscribe("t", consumer)
        for n in range(3):
            self.producer.publish("t", f"m{n}")
        self.assertTrue(self.broker.wait_for_drain())
        for consumer in consumers:
            self.assertEqual(consumer.received, ["m0", "m1", "m2"])

    def test_only_subscribers_receive(self):
        self.broker.create_topic("other")
        subscribed = RecordingConsumer("in")
        outsider = RecordingConsumer("out")
        self.broker.subscribe("t", subscribed)
        self.broker.subscribe("other", outsider)
        self.producer.publish("t", "m")
        self.assertTrue(self.broker.wait_for_drain())
        self.assertEqual(subscribed.received, ["m"])
        self.assertEqual(outsider.received, [])

    def test_a_consumer_can_listen_to_several_topics(self):
        self.broker.create_topic("t2")
        consumer = RecordingConsumer("multi")
        self.broker.subscribe("t", consumer)
        self.broker.subscribe("t2", consumer)
        self.producer.publish("t", "from-t")
        self.producer.publish("t2", "from-t2")
        self.assertTrue(self.broker.wait_for_drain())
        self.assertCountEqual(consumer.received, ["from-t", "from-t2"])

    def test_a_late_subscriber_replays_from_the_start(self):
        for n in range(3):
            self.producer.publish("t", f"m{n}")
        late = RecordingConsumer("late")
        self.broker.subscribe("t", late)
        self.assertTrue(self.broker.wait_for_drain())
        self.assertEqual(late.received, ["m0", "m1", "m2"])

    def test_subscribing_twice_is_a_no_op(self):
        consumer = RecordingConsumer("c")
        self.broker.subscribe("t", consumer)
        self.broker.subscribe("t", consumer)
        self.producer.publish("t", "m")
        self.assertTrue(self.broker.wait_for_drain())
        self.assertEqual(consumer.received, ["m"])

    def test_concurrent_producers_lose_nothing(self):
        consumer = RecordingConsumer("c")
        self.broker.subscribe("t", consumer)
        producers = [Producer(f"p{n}", self.broker) for n in range(4)]

        def burst(producer):
            for n in range(50):
                producer.publish("t", f"{producer.id}-{n}")

        threads = [threading.Thread(target=burst, args=(p,)) for p in producers]
        for t in threads: t.start()
        for t in threads: t.join()

        self.assertTrue(self.broker.wait_for_drain())
        self.assertEqual(len(consumer.received), 200)
        self.assertEqual(len(set(consumer.received)), 200)

    def test_publishing_to_an_unknown_topic_raises(self):
        with self.assertRaises(KeyError):
            self.producer.publish("nope", "m")


if __name__ == "__main__":
    unittest.main(verbosity=2)
