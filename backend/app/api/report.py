from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from backend.app.db.base import AsyncSessionLocal
from backend.app.db.models import Server, Domain, Account
from backend.app.schemas.report import (
    FullReportOut,
    ServerReport,
    DomainReport,
    AccountReport,
)

router = APIRouter(prefix="/report", tags=["Report"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/")
async def get_report(
    domain: str | None = Query(default=None),
    account: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """
    /report
    /report?domain=example.com
    /report?account=user@example.com
    """

    # --------------------------------------------------
    # 1️⃣ ACCOUNT-LEVEL REPORT (highest priority)
    # --------------------------------------------------
    if account:
        result = await db.execute(
            select(Account).where(Account.email.ilike(account))
        )
        acc = result.scalar_one_or_none()

        if not acc:
            raise HTTPException(status_code=404, detail="Account not found")

        return AccountReport(
            email=acc.email,
            local_part=acc.local_part,
            assigned_mb=acc.assigned_mb,
            used_mb=acc.used_mb,
            free_mb=acc.free_mb,
            status=acc.status,
        )

    # --------------------------------------------------
    # 2️⃣ DOMAIN-LEVEL REPORT
    # --------------------------------------------------
    if domain:
        result = await db.execute(
            select(Domain).where(Domain.name.ilike(domain))
        )
        dom = result.scalar_one_or_none()

        if not dom:
            raise HTTPException(status_code=404, detail="Domain not found")

        accounts_result = await db.execute(
            select(Account).where(Account.domain_id == dom.id)
        )
        accounts = accounts_result.scalars().all()

        return DomainReport(
            name=dom.name,
            status=dom.status,
            total_accounts=len(accounts),
            accounts=[
                AccountReport(
                    email=a.email,
                    local_part=a.local_part,
                    assigned_mb=a.assigned_mb,
                    used_mb=a.used_mb,
                    free_mb=a.free_mb,
                    status=a.status,
                )
                for a in accounts
            ],
        )

    # --------------------------------------------------
    # 3️⃣ FULL REPORT (default)
    # --------------------------------------------------
    servers_result = await db.execute(select(Server))
    servers = servers_result.scalars().all()

    server_list = []

    for server in servers:
        domains_result = await db.execute(
            select(Domain).where(Domain.server_id == server.id)
        )
        domains = domains_result.scalars().all()

        domain_list = []

        for dom in domains:
            accounts_result = await db.execute(
                select(Account).where(Account.domain_id == dom.id)
            )
            accounts = accounts_result.scalars().all()

            domain_list.append(
                DomainReport(
                    name=dom.name,
                    status=dom.status,
                    total_accounts=len(accounts),
                    accounts=[
                        AccountReport(
                            email=a.email,
                            local_part=a.local_part,
                            assigned_mb=a.assigned_mb,
                            used_mb=a.used_mb,
                            free_mb=a.free_mb,
                            status=a.status,
                        )
                        for a in accounts
                    ],
                )
            )

        server_list.append(
            ServerReport(
                name=server.name,
                hostname=server.hostname,
                cli_port=server.cli_port,
                webadmin_port=server.webadmin_port,
                username=server.username,
                domains=domain_list,
            )
        )

    return FullReportOut(
        servers=server_list,
        generated_at=datetime.utcnow(),
    )
