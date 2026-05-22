import redis
import json
from app.logger import logger

logger.info("Initialized redis connection")

redis_client = redis.Redis(
    host = "localhost",
    port = 6379,
    decode_responses=True
)

try:
    redis_client.ping()
    logger.info("Redis connected succesfully")

except Exception as e:
    logger.error(f"Redis connection failed: {str(e)}")

# save cache
def set_cache(key, value, expiry=3600):
    try:
        logger.info(f"Saving cache for key: {key}")
        
        redis_client.set(
            key, json.dumps(value), ex=expiry
        )
        logger.info("Cache stored successfully")
    except Exception as e:
        logger.error(f"Cache save failed: {str(e)}")

def get_cache(key):
    try:
        logger.info(f"Checking cache for key: {key}")
        data = redis_client.get(key)

        if data:
            logger.info("Cahce miss")
            return json.loads(data)
        logger.info("Cache miss")
        return None
    
    except Exception as e:
        logger.error(f"Cache fetch failed: {str(e)}")
        return None
    