# backend/app/schemas/jobs.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class JobBase(BaseModel):
    job_id: str
    name: str
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]

class ServerLog(BaseModel):
    server_id: str
    server_name: str
    status: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    log_text: Optional[str]

class JobDetail(JobBase):
    servers: List[ServerLog]

class ServerLogOnly(BaseModel):
    job_id: str
    server_id: str
    log_text: Optional[str]
