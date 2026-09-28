from models.errors import RateLimitExhausted
from collections import defaultdict
from core.rate_limit_strategy import FixedWindow
from core.rate_limit_strategy import RateLimitStrategy
from models.models import Client

class RateLimiter:

    def __init__(self, clients: list[Client], rate_limit_strategy: RateLimitStrategy = None):
        
        self.rate_limit_strategy = rate_limit_strategy or FixedWindow()
        self.clients: dict[str, Client] = defaultdict()
        for client in clients:
            self.clients[client.id] = client


    def allow_request(self, client_id):
        client = self.clients[client_id]
        try:
            self.rate_limit_strategy.consume_rate_limit(client)
            return True
        except RateLimitExhausted:
            return False

    def get_remaining(self, client_id):
        client = self.clients[client_id]
        return self.rate_limit_strategy.get_remaining_limit(client)

    def reset(self, client_id):
        client = self.clients[client_id]
        self.rate_limit_strategy.reset(client)