import os
import redis
from dotenv import load_dotenv

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    client.ping()
except Exception:
    client = None

def get_from_cache(short_id: str):
    if not client:
        return None
    return client.get(short_id)

def set_to_cache(short_id: str, original_url: str, ex: int = 3600):
    if not client:
        return
    client.set(short_id, original_url, ex=ex)
