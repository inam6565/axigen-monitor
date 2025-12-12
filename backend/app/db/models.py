# backend/app/db/models.py
from __future__ import annotations
import datetime
import uuid
from sqlalchemy import (
    Column, Text, Integer, Numeric, TIMESTAMP, ForeignKey, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.base import Base

class Snapshot(Base):
    __tablename__ = "snapshots"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    taken_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    source = Column(Text, nullable=True)
    servers_count = Column(Integer, nullable=True)
    domains_count = Column(Integer, nullable=True)
    accounts_count = Column(Integer, nullable=True)

class Server(Base):
    __tablename__ = "servers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    hostname = Column(Text, nullable=False)
    cli_port = Column(Integer, nullable=False, default=7000)
    webadmin_port = Column(Integer, nullable=False, default=9000)
    username = Column(Text, nullable=False)
    encrypted_password = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    domains = relationship("Domain", back_populates="server", cascade="all, delete-orphan")

class Domain(Base):
    __tablename__ = "domains"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    server_id = Column(UUID(as_uuid=True), ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    status = Column(Text, nullable=True)
    total_accounts = Column(Integer, nullable=False, default=0)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshots.id"), nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    server = relationship("Server", back_populates="domains")
    accounts = relationship("Account", back_populates="domain", cascade="all, delete-orphan")

class Account(Base):
    __tablename__ = "accounts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id", ondelete="CASCADE"), nullable=False)
    local_part = Column(Text, nullable=False)
    email = Column(Text, nullable=False, index=True)
    assigned_mb = Column(Integer, nullable=True)
    used_mb = Column(Numeric, nullable=True)
    free_mb = Column(Numeric, nullable=True)
    status = Column(Text, nullable=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshots.id"), nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    domain = relationship("Domain", back_populates="accounts")
