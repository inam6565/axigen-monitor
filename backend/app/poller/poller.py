# backend/app/poller/poller.py

import traceback
from datetime import datetime
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from backend.app.db.base import AsyncSessionLocal
from backend.app.db.models import Server, Domain, Account, Snapshot
from backend.app.utils.encrypt import decrypt_password
from sqlalchemy import text
# Axigen CLI imports
from axigen_cli.domains import list_all_domains
from axigen_cli.accounts import list_accounts_for_domain




async def poll_servers():
    """
    Main poller: iterate all servers, fetch domains & accounts,
    TRUNCATE existing Domain/Account rows per server, re-insert fresh.
    """
    print("[POLLER] Starting poll_servers()")
    async with AsyncSessionLocal() as db:
        # 1. Fetch all servers
        print("[DB] AsyncSession opened")
        print("[DB] Testing DB connection...")
        result = await db.execute(text("SELECT 1"))
        print("[DB] Connection OK, SELECT 1 returned:", result.scalar())
        servers = (await db.execute(select(Server))).scalars().all()
        print(f"[DB] Servers fetched: {len(servers)}")
        if not servers:
            print("[WARN] No servers found in DB.")
            return

        print(f"\n=== POLLER START ({datetime.now()}) ===")
        print(f"Servers detected: {len(servers)}\n")
        

        # 2. Create snapshot record
        snapshot = Snapshot(
            taken_at=datetime.utcnow(),
            source="daily-poller",
        )
        db.add(snapshot)
        await db.commit()
        await db.refresh(snapshot)

        total_domains = 0
        total_accounts = 0

        # 3. Process each server
        for server in servers:
            print(f"\n>>> Processing server: {server.name} ({server.hostname})")
            try:
                password = decrypt_password(server.encrypted_password)

                # -------------------------------
                # Fetch domains from Axigen
                # -------------------------------
                domains = list_all_domains(
                    host=server.hostname,
                    port=server.cli_port,
                    username=server.username,
                    password=password,
                )

                print(f"[OK] Domains found: {len(domains)}")

                # -------------------------------
                # Delete previous domains/accounts for this server
                # -------------------------------
                await db.execute(delete(Domain).where(Domain.server_id == server.id))
                await db.commit()

                # -------------------------------
                # Insert new domains & accounts
                # -------------------------------
                for dom in domains:
                    domain_obj = Domain(
                        name=dom["domain"],
                        server_id=server.id,
                        status=dom["status"],
                        snapshot_id=snapshot.id,
                    )
                    db.add(domain_obj)
                    await db.flush()  # to get domain_obj.id

                    # Fetch accounts & quotas
                    accounts = list_accounts_for_domain(
                        host=server.hostname,
                        port=server.cli_port,
                        username=server.username,
                        password=password,
                        domain=dom["domain"],
                        webadmin_port=server.webadmin_port,
                    )

                    for acc in accounts:
                        email = acc["email"]
                        local_part = email.split("@")[0]

                        assigned = acc.get("assigned_mb") or 0
                        used = acc.get("used_mb") or 0
                        free = assigned - used if used else assigned
                        
                        account_obj = Account(
                            domain_id=domain_obj.id,
                            local_part=local_part,
                            email=email,
                            assigned_mb=int(assigned),
                            used_mb=int(used),
                            free_mb=int(free),
                            snapshot_id=snapshot.id,
                        )
                        db.add(account_obj)

                    # Update domain total accounts
                    domain_obj.total_accounts = len(accounts)
                    total_accounts += len(accounts)

                total_domains += len(domains)
                await db.commit()
                print(f"[OK] Server processed: {server.name}")

            except Exception as e:
                print(f"[ERROR] Server failed: {server.name}")
                print(str(e))
                traceback.print_exc()
                continue

        # -------------------------------
        # Update snapshot counts
        # -------------------------------
        snapshot.servers_count = len(servers)
        snapshot.domains_count = total_domains
        snapshot.accounts_count = total_accounts
        await db.commit()

        print(f"\n=== POLLER DONE ({datetime.now()}) ===")
        print(f"Servers processed: {len(servers)}")
        print(f"Domains inserted: {total_domains}")
        print(f"Accounts inserted: {total_accounts}")
        print("=====================================\n")
