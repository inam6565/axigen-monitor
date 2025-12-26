from pydantic import BaseModel
from uuid import UUID

class DomainOut(BaseModel):
    id: UUID
    name: str
    status: str | None
    total_accounts: int

    class Config:
        from_attributes = True
