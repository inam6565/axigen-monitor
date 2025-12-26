# backend/app/api/summary.py
from fastapi import APIRouter
from sqlalchemy.future import select
from backend.app.db.base import AsyncSessionLocal
from backend.app.db.models import Server, Domain, Account, Snapshot

router = APIRouter()

@router.get("/summary/")
async def get_summary():
    async with AsyncSessionLocal() as db:
        # Servers count
        servers_result = await db.execute(select(Server))
        servers = servers_result.scalars().all()
        servers_count = len(servers)

        # Domains count
        domains_result = await db.execute(select(Domain))
        domains_count = len(domains_result.scalars().all())

        # Accounts count
        accounts_result = await db.execute(select(Account))
        accounts_count = len(accounts_result.scalars().all())

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
