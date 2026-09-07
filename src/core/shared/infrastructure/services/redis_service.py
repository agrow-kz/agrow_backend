from typing import Any

from redis.asyncio import Redis


class RedisService:
    def __init__(self, client: Redis) -> None:
        self.client = client

    async def set(self, key: str, value: Any, ttl: int) -> None:
        await self.client.setex(key, ttl, value)

    async def get(self, key: str) -> Any:
        return await self.client.get(key)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)
