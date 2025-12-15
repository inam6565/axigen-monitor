# backend/app/api/report.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from backend.app.db.base import AsyncSessionLocal
from backend.app.db.models import Server, Domain, Account
from backend.app.schemas.report import FullReportOut, ServerReport, DomainReport, AccountReport

router = APIRouter(prefix="/report", tags=["Report"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/", response_model=FullReportOut)
async def get_full_report(db: AsyncSession = Depends(get_db)):
    # Fetch all servers
    servers_result = await db.execute(select(Server))
    servers = servers_result.scalars().all()

    report_data = []
    for server in servers:
        # Fetch domains for this server
        domains_result = await db.execute(select(Domain).where(Domain.server_id == server.id))
        domains = domains_result.scalars().all()

        domain_list = []
        for domain in domains:
            # Fetch accounts for this domain
            accounts_result = await db.execute(select(Account).where(Account.domain_id == domain.id))
            accounts = accounts_result.scalars().all()

            account_list = [
                AccountReport(
                    email=a.email,
                    local_part=a.local_part,
                    assigned_mb=a.assigned_mb or 0,
                    used_mb=a.used_mb or 0,
                    free_mb=a.free_mb if a.free_mb is not None else (a.assigned_mb or 0),
                    status=a.status,
                )
                for a in accounts
            ]

            domain_list.append(
                DomainReport(
                    name=domain.name,
                    status=domain.status,
                    total_accounts=len(accounts),
                    accounts=account_list
                )
            )

        report_data.append(
            ServerReport(
                name=server.name,
                hostname=server.hostname,
                cli_port=server.cli_port,
                webadmin_port=server.webadmin_port,
                username=server.username,
                domains=domain_list
            )
        )

    return FullReportOut(
        servers=report_data,
        generated_at=datetime.utcnow()
    )
