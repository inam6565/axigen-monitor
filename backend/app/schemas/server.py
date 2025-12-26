from pydantic import BaseModel
from uuid import UUID

class ServerBase(BaseModel):
    name: str
    hostname: str
    cli_port: int
    webadmin_port: int
    username: str

class ServerOut(ServerBase):
    id: UUID

    class Config:
        from_attributes = True
