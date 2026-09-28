from core.broker import Broker
from models.consumer import Consumer
from models.producer import Producer


def main():
    broker = Broker()
    broker.create_topic("topic1")
    broker.create_topic("topic2")

    producer1 = Producer("producer1", broker)
    producer2 = Producer("producer2", broker)
    consumers = {n: Consumer(f"consumer{n}") for n in range(1, 6)}

    for n in range(1, 6):
        broker.subscribe("topic1", consumers[n])
    for n in (1, 3, 4):
        broker.subscribe("topic2", consumers[n])

    print("--- topic1: all five consumers ---")
    producer1.publish("topic1", "Message 1")
    producer1.publish("topic1", "Message 2")
    producer2.publish("topic1", "Message 3")
    broker.wait_for_drain()

    print("\n--- topic2: consumers 1, 3, 4 ---")
    producer1.publish("topic2", "Message 4")
    producer2.publish("topic2", "Message 5")
    broker.wait_for_drain()

    broker.shutdown()


if __name__ == "__main__":
    main()
