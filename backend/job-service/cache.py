"""
Redis caching layer for CQRS queries.
Implements simple caching with TTL for read operations.
"""
import os
import json
import redis
from typing import Optional, Any, Callable
from functools import wraps

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"
DEFAULT_TTL = int(os.getenv("REDIS_DEFAULT_TTL", "300"))  # 5 minutes

# Redis client (singleton)
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """Get or create Redis client."""
    global _redis_client

    if not REDIS_ENABLED:
        return None

    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            _redis_client.ping()
            print(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}. Caching disabled.")
            _redis_client = None

    return _redis_client


def cache_query(key_prefix: str, ttl: int = DEFAULT_TTL):
    """
    Decorator to cache query results in Redis.

    Args:
        key_prefix: Prefix for the cache key
        ttl: Time-to-live in seconds

    Usage:
        @cache_query("jobs:all", ttl=300)
        def get_all_jobs(self):
            return self.db.query(Job).all()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            client = get_redis_client()

            # If Redis is not available, execute function directly
            if client is None:
                return func(*args, **kwargs)

            # Generate cache key from function arguments
            key_parts = [key_prefix]

            # Add positional args (skip 'self' if present)
            for arg in args[1:]:  # Skip first arg (self)
                if hasattr(arg, '__dict__'):
                    # For query objects, use their attributes
                    key_parts.extend(str(v) for v in vars(arg).values())
                else:
                    key_parts.append(str(arg))

            # Add keyword args
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}:{v}")

            cache_key = ":".join(key_parts)

            try:
                # Try to get from cache
                cached = client.get(cache_key)
                if cached:
                    print(f"✅ Cache HIT: {cache_key}")
                    return json.loads(cached)

                print(f"⚠️ Cache MISS: {cache_key}")

                # Execute function and cache result
                result = func(*args, **kwargs)

                # Serialize result
                if result is not None:
                    # Handle SQLAlchemy models
                    if hasattr(result, '__iter__') and not isinstance(result, (str, dict)):
                        serialized = [
                            {c.name: getattr(r, c.name) for c in r.__table__.columns}
                            if hasattr(r, '__table__') else r
                            for r in result
                        ]
                    elif hasattr(result, '__table__'):
                        serialized = {c.name: getattr(result, c.name) for c in result.__table__.columns}
                    else:
                        serialized = result

                    client.setex(cache_key, ttl, json.dumps(serialized, default=str))

                return result

            except Exception as e:
                print(f"⚠️ Cache error: {e}. Executing query directly.")
                return func(*args, **kwargs)

        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    Invalidate cache keys matching a pattern.

    Args:
        pattern: Redis key pattern (e.g., "jobs:*")
    """
    client = get_redis_client()
    if client is None:
        return

    try:
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)
            print(f"✅ Invalidated {len(keys)} cache keys matching '{pattern}'")
    except Exception as e:
        print(f"⚠️ Cache invalidation error: {e}")


def clear_all_cache():
    """Clear all cache entries."""
    client = get_redis_client()
    if client is None:
        return

    try:
        client.flushdb()
        print("✅ Cleared all cache entries")
    except Exception as e:
        print(f"⚠️ Cache clear error: {e}")
