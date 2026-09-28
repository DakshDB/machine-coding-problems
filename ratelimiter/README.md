# API Rate Limiter

- Client 
    - id 
    - Plan (FREE, PRO, ENTERPRISE)

- Rate Limit Rules
    - Free - 10/min
    - Pro - 100/min
    - Enterprise - 1000/min


Operations 

- allow_request(client_id) - Bool
- get_remaining(client_id) - int
- reset(client_id) - bool

Algo 

- Fixed Window 
- Sliding Window
- Token Bucket 

