from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.base import AsyncSessionLocal
from backend.app.db.models import Account
from backend.app.schemas.account import AccountOut

router = APIRouter(prefix="/accounts", tags=["Accounts"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/domain/{domain_id}", response_model=list[AccountOut])
async def get_accounts(domain_id: str, db: AsyncSession = Depends(get_db)):
    query = select(Account).where(Account.domain_id == domain_id)
    result = await db.execute(query)
    return result.scalars().all()
