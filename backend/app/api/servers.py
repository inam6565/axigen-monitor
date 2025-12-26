from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.base import AsyncSessionLocal
from backend.app.db.models import Server
from backend.app.schemas.server import ServerOut

router = APIRouter(prefix="/servers", tags=["Servers"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/", response_model=list[ServerOut])
async def list_servers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Server))
    servers = result.scalars().all()
    return servers
