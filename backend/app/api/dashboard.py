from fastapi import APIRouter, Depends
from sqlalchemy import func
from backend.app.db.base import AsyncSessionLocal
from backend.app.db.models import Server, Domain, Account

router = APIRouter()

@router.get("/stats")
async def get_stats():
    async with AsyncSessionLocal() as db:
        servers = (await db.execute(func.count(Server.id))).scalar() or 0
        domains = (await db.execute(func.count(Domain.id))).scalar() or 0
        accounts = (await db.execute(func.count(Account.id))).scalar() or 0

    return {"servers": servers, "domains": domains, "accounts": accounts}
