class Consumer:
    def __init__(self, consumer_id):
        self.id = consumer_id

    def consume(self, message):
        print(f"{self.id} received {message}")
