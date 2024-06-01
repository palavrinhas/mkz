import time
from functools import wraps

def rate_limited(limit=1, interval=3):
    def decorator(func):
        requests = {}  

        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id")
            current_time = time.time()

            nonlocal requests
            if user_id in requests:
                while requests[user_id] and requests[user_id][0] < current_time - interval:
                    requests[user_id].pop(0)

            if user_id in requests and len(requests[user_id]) >= limit:
                return "Limite de solicitações excedido."

            requests.setdefault(user_id, []).append(current_time)

            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator
