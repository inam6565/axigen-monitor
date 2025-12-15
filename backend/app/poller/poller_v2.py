# backend/app/poller/poller_v2.py
from __future__ import annotations

import asyncio
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, List, Set

from sqlalchemy import select, delete, text, func
from sqlalchemy.dialects.postgresql import insert

from backend.app.db.base import AsyncSessionLocal
from backend.app.db.models import Server, Domain, Account, DomainChange, AccountChange, Snapshot
from backend.app.utils.encrypt import decrypt_password

from axigen_cli.domains import list_all_domains
from axigen_cli.tsv import _fetch_webadmin_accounts, prepare_from_tsv_rows
from axigen_cli.controller import ServerConfig
from axigen_cli.controller_stream import process_server_domains_stream




def _now_utc():
    return datetime.now(timezone.utc)


async def _insert_domain_changes(db, rows: List[Dict[str, Any]]):
    if not rows:
        return
    await db.execute(insert(DomainChange).values(rows))
    await db.commit()

async def _write_snapshot(db, source: str = "poller_v2"):
    now = _now_utc()

    servers_count = (await db.execute(select(func.count(Server.id)))).scalar_one()
    domains_count = (await db.execute(select(func.count(Domain.id)))).scalar_one()
    accounts_count = (await db.execute(select(func.count(Account.id)))).scalar_one()

    snap = Snapshot(
        taken_at=now,
        source=source,
        servers_count=int(servers_count),
        domains_count=int(domains_count),
        accounts_count=int(accounts_count),
    )
    db.add(snap)
    await db.commit()


async def _insert_account_changes(db, rows: List[Dict[str, Any]]):
    if not rows:
        return
    await db.execute(insert(AccountChange).values(rows))
    await db.commit()


async def _upsert_domains_and_get_map(
    db,
    server_id,
    cli_domains: List[Dict[str, Any]],
) -> Dict[str, Any]:
    seen_domains: Set[str] = set()
    status_by_domain: Dict[str, str] = {}

    for d in cli_domains:
        name = (d.get("domain") or d.get("name") or "").strip().lower()
        if not name:
            continue
        status = (d.get("status") or "").strip()
        seen_domains.add(name)
        status_by_domain[name] = status

    now = _now_utc()

    # Load existing statuses to detect changes + additions
    existing_rows = await db.execute(
        select(Domain.name, Domain.status).where(Domain.server_id == server_id)
    )
    existing_status = {name.lower(): (status or "") for (name, status) in existing_rows.all()}

    domain_change_rows: List[Dict[str, Any]] = []

    # Upsert domains
    rows = []
    for name in sorted(seen_domains):
        new_status = status_by_domain.get(name) or ""
        old_status = existing_status.get(name)

        if old_status is None:
            domain_change_rows.append(
                {
                    "server_id": server_id,
                    "domain_name": name,
                    "event_type": "DOMAIN_ADDED",
                    "old_status": None,
                    "new_status": new_status,
                    "happened_at": now,
                }
            )
        else:
            if (old_status or "") != (new_status or ""):
                domain_change_rows.append(
                    {
                        "server_id": server_id,
                        "domain_name": name,
                        "event_type": "DOMAIN_STATUS_CHANGED",
                        "old_status": old_status,
                        "new_status": new_status,
                        "happened_at": now,
                    }
                )

        rows.append(
            {
                "server_id": server_id,
                "name": name,
                "status": new_status,
                "last_seen_at": now,
                # optional state_hash (status only for now)
                "state_hash": new_status,
            }
        )

    if rows:
        stmt = insert(Domain).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_domains_server_id_name",
            set_={
                "status": stmt.excluded.status,
                "last_seen_at": stmt.excluded.last_seen_at,
                "state_hash": stmt.excluded.state_hash,
                "updated_at": text("now()"),
            },
        )
        await db.execute(stmt)
        await db.commit()

    # Write domain changes
    await _insert_domain_changes(db, domain_change_rows)

    # Fetch domain ids
    result = await db.execute(select(Domain.id, Domain.name).where(Domain.server_id == server_id))
    domain_id_by_name = {name: did for (did, name) in result.all()}

    return {
        "domain_id_by_name": domain_id_by_name,
        "status_by_domain": status_by_domain,
        "seen_domains": seen_domains,
    }


async def _delete_missing_domains(db, server_id, seen_domains: Set[str]):
    result = await db.execute(select(Domain.id, Domain.name).where(Domain.server_id == server_id))
    existing = {(name.lower(), did) for (did, name) in result.all()}

    now = _now_utc()
    to_delete = [(name, did) for (name, did) in existing if name not in seen_domains]
    if not to_delete:
        return

    # Log deletions
    await _insert_domain_changes(
        db,
        [
            {
                "server_id": server_id,
                "domain_name": name,
                "event_type": "DOMAIN_DELETED",
                "old_status": None,
                "new_status": None,
                "happened_at": now,
            }
            for (name, _did) in to_delete
        ],
    )

    to_delete_ids = [did for (_name, did) in to_delete]
    await db.execute(delete(Domain).where(Domain.id.in_(to_delete_ids)))
    await db.commit()



def _is_domain_disabled(status: str) -> bool:
    """
    Adjust this logic to match your Axigen status strings.
    If you have exact statuses (e.g. 'enabled', 'disabled', 'locked'), map accordingly.
    """
    s = (status or "").lower()
    if not s:
        return False
    return any(k in s for k in ["disabled", "locked", "suspended"])


async def _delete_accounts_for_disabled_domains(
    db,
    server_id,
    domain_id_by_name: Dict[str, Any],
    status_by_domain: Dict[str, str],
):
    """
    If domain is disabled/locked, TSV won't show it. You decided: delete its accounts.
    """
    disabled_domain_ids = []
    for dom, did in domain_id_by_name.items():
        if _is_domain_disabled(status_by_domain.get(dom, "")):
            disabled_domain_ids.append(did)

    if disabled_domain_ids:
        await db.execute(delete(Account).where(Account.domain_id.in_(disabled_domain_ids)))
        await db.commit()


async def _db_writer_consume_domain_results(
    db,
    server_id,
    domain_id_by_name: Dict[str, Any],
    queue: asyncio.Queue,
    processed_domains: Set[str],
):
    """
    Streaming DB writer: consumes DomainResult items until sentinel None is received.
    For each domain result:
      - upsert accounts (assigned_mb + used_mb always)
      - update Domain.total_accounts
      - track seen accounts for deletion
    After completion:
      - delete missing accounts for each processed domain (immediate delete)
    """
    now = _now_utc()
    seen_accounts_by_domain: Dict[str, Set[str]] = {d: set() for d in processed_domains}

    # Buffering for batch upserts
    acc_rows_buffer: List[Dict[str, Any]] = []
    flush_accounts_threshold = 2000  # tune as needed

    async def flush_accounts():
        nonlocal acc_rows_buffer
        if not acc_rows_buffer:
            return
        stmt = insert(Account).values(acc_rows_buffer)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_accounts_domain_id_local_part",
            set_={
                "email": stmt.excluded.email,
                "assigned_mb": stmt.excluded.assigned_mb,
                "used_mb": stmt.excluded.used_mb,
                "free_mb": stmt.excluded.free_mb,
                "last_seen_at": stmt.excluded.last_seen_at,
                "quota_hash": stmt.excluded.quota_hash,
                "updated_at": text("now()"),
            },
        )
        await db.execute(stmt)
        await db.commit()
        acc_rows_buffer = []

    while True:
        item = await queue.get()
        if item is None:
            break

        domain = (item.get("domain") or "").strip().lower()
        accounts = item.get("accounts") or []

        if domain not in domain_id_by_name:
            # Domain might be missing if CLI list and TSV differ; skip safely
            continue

        domain_id = domain_id_by_name[domain]

        # Update domain total_accounts (current)
        await db.execute(
            text("UPDATE domains SET total_accounts = :n, updated_at = now() WHERE id = :id"),
            {"n": len(accounts), "id": str(domain_id)},
        )

        for acc in accounts:
            email = (acc.get("email") or "").strip().lower()
            if not email or "@" not in email:
                continue
            local_part = email.split("@", 1)[0].strip()
            seen_accounts_by_domain.setdefault(domain, set()).add(local_part)

            assigned_mb = acc.get("assigned_mb")
            used_mb = acc.get("used_mb")

            # Normalize numeric types
            assigned_mb = int(assigned_mb) if assigned_mb is not None else None
            used_mb = float(used_mb) if used_mb is not None else None

            # Free MB: only meaningful if assigned_mb is set
            free_mb = None
            if assigned_mb is not None and used_mb is not None:
                free_mb = assigned_mb - used_mb

            # quota_hash: hash only assigned_mb (not used_mb)
            quota_hash = None if assigned_mb is None else str(assigned_mb)

            acc_rows_buffer.append(
                {
                    "domain_id": domain_id,
                    "local_part": local_part,
                    "email": email,
                    "assigned_mb": assigned_mb,
                    "used_mb": used_mb,
                    "free_mb": free_mb,
                    "last_seen_at": now,
                    "quota_hash": quota_hash,
                }
            )

        if len(acc_rows_buffer) >= flush_accounts_threshold:
            await flush_accounts()

    # Final flush
    await flush_accounts()
    await db.commit()

    # Deletion pass: accounts missing from processed domains
    for domain in processed_domains:
        if domain not in domain_id_by_name:
            continue
        domain_id = domain_id_by_name[domain]
        seen_local_parts = seen_accounts_by_domain.get(domain, set())

        # If domain had no accounts, delete all
        if not seen_local_parts:
            await db.execute(delete(Account).where(Account.domain_id == domain_id))
            continue

        await db.execute(
            delete(Account).where(
                (Account.domain_id == domain_id) & (~Account.local_part.in_(list(seen_local_parts)))
            )
        )

    await db.commit()


async def poll_servers_v2(max_workers_per_server: int = 10):
    """
    Poller v2:
      - servers sequentially
      - within server, domains processed concurrently by controller
      - DB writer consumes results streaming
      - maintains current-state tables (domains/accounts)
    """
    print("[POLLER_V2] Starting", datetime.now())

    async with AsyncSessionLocal() as db:
        # sanity test
        _ = await db.execute(text("SELECT 1"))

        servers = (await db.execute(select(Server))).scalars().all()
        print(f"[POLLER_V2] Servers found: {len(servers)}")
        if not servers:
            return

        for server in servers:
            print(f"\n>>> [SERVER] {server.name} ({server.hostname})")

            try:
                password = decrypt_password(server.encrypted_password)

                # 1) CLI domain inventory (includes disabled)
                cli_domains = list_all_domains(
                    host=server.hostname,
                    port=server.cli_port,
                    username=server.username,
                    password=password,
                )
                print(f"[CLI] domains={len(cli_domains)}")

                up = await _upsert_domains_and_get_map(db, server.id, cli_domains)
                domain_id_by_name = up["domain_id_by_name"]
                status_by_domain = up["status_by_domain"]
                seen_domains = up["seen_domains"]

                # delete domains not in CLI list
                await _delete_missing_domains(db, server.id, seen_domains)

                # delete accounts for disabled/locked domains
                await _delete_accounts_for_disabled_domains(db, server.id, domain_id_by_name, status_by_domain)

                # 2) Fetch TSV once
                rows = await _fetch_webadmin_accounts(
                    host=server.hostname,
                    port=server.webadmin_port,
                    user=server.username,
                    password=password,
                )
                if rows is None:
                    print("[TSV] FAILED (skipping account updates/deletes for active domains)")
                    continue

                prepared = prepare_from_tsv_rows(rows)
                active_domains = set([d.strip().lower() for d in prepared.get("domains", [])])

                # Only process domains that exist in CLI list and are TSV-visible
                domains_to_process = sorted(active_domains.intersection(seen_domains))
                print(f"[TSV] domains={len(active_domains)} | process={len(domains_to_process)}")

                # 3) Streaming queue + DB writer task
                q: asyncio.Queue = asyncio.Queue(maxsize=500)
                writer_task = asyncio.create_task(
                    _db_writer_consume_domain_results(
                        db=db,
                        server_id=server.id,
                        domain_id_by_name=domain_id_by_name,
                        queue=q,
                        processed_domains=set(domains_to_process),
                    )
                )

                loop = asyncio.get_running_loop()

                def on_result(res: Dict[str, Any]) -> None:
                    # called from threadpool thread; push into asyncio queue safely
                    loop.call_soon_threadsafe(q.put_nowait, res)

                # 4) Run controller in a thread (so poller remains async)
                server_cfg = ServerConfig(
                    host=server.hostname,
                    cli_port=server.cli_port,
                    username=server.username,
                    password=password,
                    cli_timeout=8.0,
                )

                summary = await asyncio.to_thread(
                    process_server_domains_stream,
                    server_cfg,
                    prepared,
                    on_result,
                    max_workers_per_server,
                    domains_to_process,
                )

                # signal completion to writer
                await q.put(None)
                await writer_task
                
                print(f"[SERVER DONE] {server.name} summary={summary}")

            except Exception as e:
                print(f"[ERROR] Server failed: {server.name}")
                print(str(e))
                traceback.print_exc()
                continue
        await _write_snapshot(db, source="poller_v2")
    print("[POLLER_V2] Done", datetime.now())
