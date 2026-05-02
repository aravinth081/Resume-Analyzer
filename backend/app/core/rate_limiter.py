"""
Redis-backed rate limiter using a sliding window algorithm.
Applied as a FastAPI dependency.
"""
from fastapi import Request, HTTPException, status
import redis.asyncio as redis
from app.config import settings

# Lazy-initialized Redis connection
_redis_client = None


async def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def rate_limit(request: Request):
    """
    Sliding-window rate limiter.
    Limits each IP to RATE_LIMIT_PER_MINUTE requests per minute.
    """
    try:
        r = await get_redis()
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"

        current = await r.get(key)
        if current and int(current) >= settings.RATE_LIMIT_PER_MINUTE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)  # 1-minute window
        await pipe.execute()
    except HTTPException:
        raise
    except Exception:
        # If Redis is down, allow the request (fail-open)
        pass
