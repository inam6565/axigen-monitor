from __future__ import annotations

import uuid
from sqlalchemy import (
    Column,
    Text,
    Integer,
    Numeric,
    TIMESTAMP,
    ForeignKey,
    func,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


class Snapshot(Base):
    """
    Optional poll-run marker. Keep it for now.
    In the new workflow, Domain/Account won't rely on snapshot_id.
    """
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
    __table_args__ = (
        UniqueConstraint("server_id", "name", name="uq_domains_server_id_name"),
        Index("ix_domains_server_id", "server_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    server_id = Column(UUID(as_uuid=True), ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)

    status = Column(Text, nullable=True)
    total_accounts = Column(Integer, nullable=False, default=0)

    # NEW: current-state fields
    last_seen_at = Column(TIMESTAMP(timezone=True), nullable=True)
    state_hash = Column(Text, nullable=True)

    # OLD: keep for now (later migration can drop)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshots.id"), nullable=True)

    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    server = relationship("Server", back_populates="domains")
    accounts = relationship("Account", back_populates="domain", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("domain_id", "local_part", name="uq_accounts_domain_id_local_part"),
        Index("ix_accounts_domain_id", "domain_id"),
        Index("ix_accounts_email", "email"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id", ondelete="CASCADE"), nullable=False)

    local_part = Column(Text, nullable=False)
    email = Column(Text, nullable=False)

    assigned_mb = Column(Integer, nullable=True)
    used_mb = Column(Numeric, nullable=True)
    free_mb = Column(Numeric, nullable=True)

    # NEW: current-state fields
    last_seen_at = Column(TIMESTAMP(timezone=True), nullable=True)
    quota_hash = Column(Text, nullable=True)

    # OLD: keep for now
    status = Column(Text, nullable=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshots.id"), nullable=True)

    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    domain = relationship("Domain", back_populates="accounts")


class DomainChange(Base):
    __tablename__ = "domain_changes"
    __table_args__ = (
        Index("ix_domain_changes_server_id_happened_at", "server_id", "happened_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    server_id = Column(UUID(as_uuid=True), ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    domain_name = Column(Text, nullable=False)

    event_type = Column(Text, nullable=False)  # DOMAIN_ADDED / DOMAIN_DELETED / DOMAIN_STATUS_CHANGED
    old_status = Column(Text, nullable=True)
    new_status = Column(Text, nullable=True)

    happened_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    run_id = Column(UUID(as_uuid=True), ForeignKey("snapshots.id"), nullable=True)


class AccountChange(Base):
    __tablename__ = "account_changes"
    __table_args__ = (
        Index("ix_account_changes_server_id_happened_at", "server_id", "happened_at"),
        Index("ix_account_changes_email_happened_at", "email", "happened_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    server_id = Column(UUID(as_uuid=True), ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    domain_name = Column(Text, nullable=False)

    email = Column(Text, nullable=False)
    local_part = Column(Text, nullable=False)

    event_type = Column(Text, nullable=False)  # ACCOUNT_ADDED / ACCOUNT_DELETED / QUOTA_CHANGED
    old_assigned_mb = Column(Integer, nullable=True)
    new_assigned_mb = Column(Integer, nullable=True)

    happened_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    run_id = Column(UUID(as_uuid=True), ForeignKey("snapshots.id"), nullable=True)
