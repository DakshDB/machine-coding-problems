from core.rate_limit_strategy import MovingWindow
from time import sleep
from core.rate_limiter import RateLimiter
from models.models import Client, RateLimitPlan
if __name__ == '__main__':
    
    print("Rate Limiter")

    freeClient = Client("1", RateLimitPlan.FREE)

    rate_limiter = RateLimiter(clients=[freeClient], rate_limit_strategy=MovingWindow())

    remaining_limit = rate_limiter.get_remaining(freeClient.id)
    print(f"Remaining Rate Limit for {freeClient.id} is {remaining_limit}")

    for i in range(0, 11):
        is_allow = rate_limiter.allow_request(freeClient.id)
        print(f"Request for {i} client - {freeClient.id} is {is_allow}")

        if i>1 and i%7 == 0:
            # rate_limiter.reset(client_id=freeClient.id)
            sleep(70)


    remaining_limit = rate_limiter.get_remaining(freeClient.id)
    print(f"Remaining Rate Limit for {freeClient.id} is {remaining_limit}")
