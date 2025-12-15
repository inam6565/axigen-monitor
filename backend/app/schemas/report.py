# backend/app/schemas/report.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AccountReport(BaseModel):
    email: str
    local_part: str
    assigned_mb: Optional[int]
    used_mb: Optional[int]
    free_mb: Optional[int]
    status: Optional[str]

class DomainReport(BaseModel):
    name: str
    status: Optional[str]
    total_accounts: int
    accounts: List[AccountReport]

class ServerReport(BaseModel):
    name: str
    hostname: str
    cli_port: int
    webadmin_port: int
    username: str
    domains: List[DomainReport]

class FullReportOut(BaseModel):
    servers: List[ServerReport]
    generated_at: datetime
