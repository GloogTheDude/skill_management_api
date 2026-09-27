import os
import secrets


SESSION_COOKIE_NAME = "session_id"
SESSION_KEY_PREFIX = "session:"
SESSION_TTL_SECONDS = int(os.getenv("AUTH_SESSION_TTL_SECONDS", "3600"))
AUTH_COOKIE_SECURE = os.getenv("AUTH_COOKIE_SECURE", "false").lower() == "true"
AUTH_COOKIE_SAMESITE = os.getenv("AUTH_COOKIE_SAMESITE", "lax")


class RedisSessionStore:
    def __init__(self, redis):
        self.redis = redis

    @staticmethod
    def _key(session_id: str) -> str:
        return f"{SESSION_KEY_PREFIX}{session_id}"

    async def create(self, id_employee: int) -> str:
        session_id = secrets.token_urlsafe(32)
        await self.redis.set(
            self._key(session_id),
            str(id_employee),
            ex=SESSION_TTL_SECONDS,
        )
        return session_id

    async def get_employee_id(self, session_id: str) -> int | None:
        value = await self.redis.get(self._key(session_id))
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    async def delete(self, session_id: str) -> None:
        await self.redis.delete(self._key(session_id))
