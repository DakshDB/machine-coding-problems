from enum import Enum

# Enums
class RateLimitPlan(Enum):
    FREE = 'free'
    PRO = 'pro'
    ENTERPRISE = 'enterprise'


class Client:
    def __init__(self, id: str, plan: RateLimitPlan = RateLimitPlan.FREE):
        self.id = id
        self.plan = plan

