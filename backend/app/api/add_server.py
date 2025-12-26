from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.base import AsyncSessionLocal
from backend.app.db.models import Server
from backend.app.schemas.add_server import ServerCreate, ResponseMessage
from backend.app.utils.encrypt import encrypt_password

router = APIRouter(prefix="/add_server", tags=["AddServers"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=ResponseMessage)
async def add_server(payload: ServerCreate, db: AsyncSession = Depends(get_db)):
    # Prevent duplicate hostname
    existing = await db.execute(
        select(Server).where(Server.hostname == payload.hostname)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Server already exists")

    server = Server(
        name=payload.name,
        hostname=payload.hostname,
        cli_port=payload.cli_port,
        webadmin_port=payload.webadmin_port,
        username=payload.username,
        encrypted_password=encrypt_password(payload.password),
    )

    db.add(server)
    await db.commit()

    # Return a simple success message
    return ResponseMessage(success=True, message="Server added successfully")
