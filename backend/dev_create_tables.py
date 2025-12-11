# quick create script, run once
import asyncio
from app.db.base import engine
from app.db import models

async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

asyncio.run(create_all())
