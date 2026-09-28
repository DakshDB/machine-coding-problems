from datetime import timedelta
from models.errors import RateLimitExhausted
from models.constants import RATE_LIMIT_RULES_PER_MIN
from models.models import Client
from datetime import datetime
from abc import abstractmethod
from abc import ABC

class RateLimitStrategy(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_remaining_limit(self, client: Client):
        pass

    @abstractmethod
    def consume_rate_limit(self, client: Client):
        pass

    @abstractmethod
    def reset(self, client: Client):
        pass

class FixedWindow(RateLimitStrategy):
    
    def __init__(self):
        super().__init__()
        self.client_rate_limit: dict[str, dict] = {}

    def _get_client_rate_limit(self, client: Client):
        rate_limit_per_min = RATE_LIMIT_RULES_PER_MIN[client.plan]

        client_rate_limit = self.client_rate_limit.get(client.id, {
                "timestamp": datetime.now().replace(second=0, microsecond=0),
                "limit_remaining": rate_limit_per_min
            })
        current_time = datetime.now().replace(second=0, microsecond=0)
        if current_time != client_rate_limit["timestamp"]:
            client_rate_limit = {
                "timestamp": datetime.now().replace(second=0, microsecond=0),
                "limit_remaining": rate_limit_per_min
            }
            self.client_rate_limit[client.id] = client_rate_limit


        return client_rate_limit

    def get_remaining_limit(self, client: Client):
        client_rate_limit = self._get_client_rate_limit(client)
        limit_remaining = client_rate_limit['limit_remaining']
        return limit_remaining

    def consume_rate_limit(self, client: Client):

        client_rate_limit = self._get_client_rate_limit(client)

        if client_rate_limit['limit_remaining'] > 0:
            client_rate_limit['limit_remaining'] = client_rate_limit['limit_remaining'] - 1
            self.client_rate_limit[client.id] = client_rate_limit
        else:
            raise RateLimitExhausted()

    def reset(self, client: Client):
        self.client_rate_limit.pop(client.id, None)



class MovingWindow(RateLimitStrategy):
    
    def __init__(self):
        super().__init__()
        self.client_requests: dict[str, list] = {}

    
    def _get_client_requests_last_min(self, client: Client):
        
        client_requests = self.client_requests.get(client.id, [])

        # Filter last min request
        current_time = datetime.now()
        last_min = current_time - timedelta(minutes=1)
        client_requests = [client_request for client_request in client_requests if client_request > last_min ]
        self.client_requests[client.id] = client_requests

        return client_requests

    def get_remaining_limit(self, client: Client):
        rate_limit_per_min = RATE_LIMIT_RULES_PER_MIN[client.plan]

        client_requests = self._get_client_requests_last_min(client)

        return rate_limit_per_min - len(client_requests)

    def consume_rate_limit(self, client: Client):
    
        remaining_limit = self.get_remaining_limit(client)

        if remaining_limit > 0:
            self.client_requests[client.id].append(
                datetime.now()
            )
        else:
            raise RateLimitExhausted()

    def reset(self, client: Client):
    
        self.client_requests.pop(client.id, None)







