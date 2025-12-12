from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.base import AsyncSessionLocal
from backend.app.db.models import Domain
from backend.app.schemas.domain import DomainOut

router = APIRouter(prefix="/domains", tags=["Domains"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/server/{server_id}", response_model=list[DomainOut])
async def get_domains(server_id: str, db: AsyncSession = Depends(get_db)):
    query = select(Domain).where(Domain.server_id == server_id)
    result = await db.execute(query)
    return result.scalars().all()
