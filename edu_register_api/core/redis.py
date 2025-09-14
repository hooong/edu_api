import redis
from contextlib import contextmanager
from typing import Generator
from uuid import uuid4
import time

from edu_register_api.core.config import settings


class RedisClient:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

    def ping(self) -> bool:
        try:
            return self.redis.ping()
        except Exception:
            return False

    @contextmanager
    def lock(
        self,
        lock_key: str,
        timeout: int = settings.REDIS_LOCK_TIMEOUT,
        blocking_timeout: int = settings.REDIS_LOCK_BLOCKING_TIMEOUT,
    ) -> Generator[bool, None, None]:
        lock_value = str(uuid4())
        acquired = False

        try:
            start_time = time.time()

            while time.time() - start_time < blocking_timeout:
                acquired = self.redis.set(
                    lock_key,
                    lock_value,
                    nx=True,
                    ex=timeout,
                )

                if acquired:
                    break

                time.sleep(0.1)
            yield acquired

        finally:
            if acquired:
                self._release_lock(lock_key, lock_value)

    def _release_lock(self, lock_key: str, lock_value: str) -> bool:
        lua_script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
        """

        try:
            result = self.redis.eval(lua_script, 1, lock_key, lock_value)
            return bool(result)
        except Exception:
            return False


redis_client = RedisClient()
