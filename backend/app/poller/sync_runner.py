from sqlalchemy.orm import Session
from app.db.models import Server, Domain, Account
from app.poller.fetcher import fetch_domains, fetch_domain_accounts


def truncate_tables(db: Session):
    db.query(Account).delete()
    db.query(Domain).delete()
    db.commit()


def sync_all_servers(db: Session):
    servers = db.query(Server).all()

    truncate_tables(db)

    for server in servers:
        print(f"[SYNC] Server: {server.name}")

        # 1. Fetch domains
        domains = fetch_domains(server)

        for d in domains:
            domain_obj = Domain(
                domain=d,
                server_id=server.id,
                status=True  # later update when we fetch real status
            )
            db.add(domain_obj)
            db.flush()

            # 2. Fetch accounts for each domain
            accounts = fetch_domain_accounts(server, d)
            domain_obj.total_accounts = len(accounts)

            for acc in accounts:
                free_mb = None
                if acc["assigned_mb"] and acc["used_mb"]:
                    free_mb = "N/A"  # can compute later

                db.add(Account(
                    email=acc["email"],
                    assigned_mb=acc["assigned_mb"],
                    used_mb=acc["used_mb"],
                    free_mb=free_mb,
                    domain_id=domain_obj.id
                ))

        db.commit()

    print("[SYNC] Completed")
