import json
from datetime import timedelta
import redis
from app.config import settings

redis_client = redis.from_url(settings.redis_url)

class ProgressManager:
    @staticmethod
    def publish(job_id: str, agent: str, status: str, **kwargs):
        """
        Publishes progress state to Redis with a TTL.
        This is read by the FastAPI SSE endpoint.
        """
        key = f"job:{job_id}:progress"
        data = {
            "agent": agent,
            "status": status,
            **kwargs
        }
        # Keep progress in Redis for 24 hours
        redis_client.setex(key, timedelta(hours=24), json.dumps(data))

    @staticmethod
    def get(job_id: str) -> dict | None:
        """
        Retrieves current progress from Redis.
        """
        key = f"job:{job_id}:progress"
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
