from arq import ArqRedis


class ArqService:
    def __init__(self, pool: ArqRedis):
        self.pool = pool

    async def enqueue(self, task_name: str, **kwargs) -> None:
        await self.pool.enqueue_job(task_name, **kwargs)
