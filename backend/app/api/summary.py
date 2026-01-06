# backend/app/api/summary.py
from fastapi import APIRouter
from sqlalchemy.future import select
from sqlalchemy import func, select
from backend.app.db.base import AsyncSessionLocal
from backend.app.db.models import Server, Domain, Account, Snapshot

router = APIRouter()

@router.get("/summary/")
async def get_summary():
    async with AsyncSessionLocal() as db:
        # Servers count
        servers_count_result = await db.execute(select(func.count(Server.id)))
        servers_count = servers_count_result.scalar() or 0

        # Domains count
        domains_count_result = await db.execute(select(func.count(Domain.id)))
        domains_count = domains_count_result.scalar() or 0

        # Accounts count
        accounts_count_result = await db.execute(select(func.count(Account.id)))
        accounts_count = accounts_count_result.scalar() or 0

        # Last snapshot
        snapshot_result = await db.execute(
            select(Snapshot).order_by(Snapshot.taken_at.desc())
        )
        last_snapshot = snapshot_result.scalars().first()
        last_snapshot_time = last_snapshot.taken_at if last_snapshot else None

        return {
            "servers_count": servers_count,
            "domains_count": domains_count,
            "accounts_count": accounts_count,
            "last_snapshot_time": last_snapshot_time,
        }