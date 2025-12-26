from pydantic import BaseModel
from uuid import UUID

class AccountOut(BaseModel):
    id: UUID
    email: str
    assigned_mb: int | None
    used_mb: float | None
    free_mb: float | None

    class Config:
        from_attributes = True
