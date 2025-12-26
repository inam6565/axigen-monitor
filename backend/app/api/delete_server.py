from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.base import AsyncSessionLocal
from backend.app.db.models import Server
from backend.app.schemas.delete_server import DeleteServerRequest, ResponseMessage

router = APIRouter(prefix="/delete_server/", tags=["DeleteServer"])

# Dependency to get async DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.delete("", response_model=ResponseMessage)
async def delete_server_api(payload: DeleteServerRequest, db: AsyncSession = Depends(get_db)):
    # Check if server exists first
    query = await db.execute(select(Server).where(Server.hostname == payload.hostname))
    server = query.scalar_one_or_none()

    if not server:
        return ResponseMessage(success=False, message=f"No server found with hostname: {payload.hostname}")

    # Delete server
    stmt = delete(Server).where(Server.hostname == payload.hostname)
    await db.execute(stmt)
    await db.commit()

    return ResponseMessage(success=True, message=f"Deleted server with hostname: {payload.hostname}")
