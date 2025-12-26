# backend/app/api/jobs.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
from datetime import datetime, timezone
import asyncio
from typing import List

from backend.app.db.base import AsyncSessionLocal
from backend.app.db.models import Job, JobLog, Server
from backend.app.schemas.jobs import JobBase, JobDetail, ServerLog, ServerLogOnly
from backend.app.poller.poller_v3 import poll_servers_v3

router = APIRouter(prefix="/jobs", tags=["Jobs"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# -----------------------
# POST /jobs/run
# -----------------------
@router.post("/run")
async def create_job(max_parallel_servers: int = 3, db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    job_id = str(uuid4())
    job_name = f"Poll-{now.strftime('%Y-%m-%d-%H:%M:%S')}"

    job = Job(
        id=job_id,
        name=job_name,
        status="PENDING",
        created_at=now,
        max_parallel_servers=max_parallel_servers,
        keep_logs_days=7,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    servers_result = await db.execute(select(Server.id, Server.name))
    servers = servers_result.all()

    for server_id, server_name in servers:
        job_log = JobLog(
            id=str(uuid4()),
            job_id=job_id,
            server_id=server_id,
            status="PENDING",
            started_at=None,
            finished_at=None,
            log_text=None,
        )
        db.add(job_log)

    await db.commit()

    asyncio.create_task(poll_servers_v3(job_id, max_workers_per_server=max_parallel_servers))

    return {
        "job_id": job_id,
        "name": job_name,
        "servers_count": len(servers),
        "message": "Job and JobLogs created successfully, poller started in background"
    }

# -----------------------
# GET /jobs
# -----------------------
@router.get("", response_model=List[JobBase])
async def get_jobs(limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).order_by(Job.created_at.desc()).limit(limit))
    jobs = result.scalars().all()
    return [
        JobBase(
            job_id=str(job.id),
            name=job.name,
            status=job.status,
            created_at=job.created_at,
            started_at=job.started_at,
            finished_at=job.finished_at,
        ) for job in jobs
    ]

# -----------------------
# GET /jobs/{job_id}  - job detail with server logs
# -----------------------
@router.get("/{job_id}", response_model=JobDetail)
async def get_job_detail(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    result = await db.execute(
        select(JobLog, Server.name).join(Server, Server.id == JobLog.server_id).where(JobLog.job_id == job_id)
    )
    server_logs = [
        ServerLog(
            server_id=str(log.JobLog.server_id),
            server_name=log.name,
            status=log.JobLog.status,
            started_at=log.JobLog.started_at,
            finished_at=log.JobLog.finished_at,
            log_text=log.JobLog.log_text,
        )
        for log in result.all()
    ]

    return JobDetail(
        job_id=str(job.id),
        name=job.name,
        status=job.status,
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
        servers=server_logs,
    )

# -----------------------
# GET /jobs/{job_id}/servers/{server_id}/log
# -----------------------
@router.get("/{job_id}/servers/{server_id}/log", response_model=ServerLogOnly)
async def get_server_log(job_id: str, server_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(JobLog).where(JobLog.job_id == job_id, JobLog.server_id == server_id)
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Server log not found")
    return ServerLogOnly(
        job_id=str(job_id),
        server_id=str(server_id),
        log_text=log.log_text,
    )
