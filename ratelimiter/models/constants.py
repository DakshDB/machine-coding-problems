from models.models import RateLimitPlan

RATE_LIMIT_RULES_PER_MIN = {
    RateLimitPlan.FREE:  10,
    RateLimitPlan.PRO: 100,
    RateLimitPlan.ENTERPRISE: 1000
}