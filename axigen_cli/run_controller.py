# axigen_cli/runner_controller.py

import asyncio
import getpass
from pprint import pprint

from axigen_cli.tsv import _fetch_webadmin_accounts, prepare_from_tsv_rows
from axigen_cli.controller import ServerConfig, process_server_domains


async def main():
    # ---- Axigen CLI ----
    host = input("Axigen host: ").strip()
    cli_port = int(input("Axigen port [7000]: ").strip() or "7000")
    username = input("Axigen username: ").strip()
    password = getpass.getpass("Axigen password: ")

    # ---- WebAdmin ----
    #wa_host_in = input("WebAdmin host (or 'same'): ").strip()
    #wa_host = host if wa_host_in.lower() in {"same", ""} else wa_host_in
    wa_port = int(input("WebAdmin port: ").strip())
    #wa_user = input("WebAdmin username: ").strip()
    #wa_pass = getpass.getpass("WebAdmin password: ")

    max_workers = int(input("Worker threads [10]: ").strip() or "10")

    print("\n[INFO] Fetching WebAdmin TSV...\n")
    rows = await _fetch_webadmin_accounts(
        host=host,
        port=wa_port,
        user=username,
        password=password,
    )
    if rows is None:
        print("[ERROR] Failed to fetch WebAdmin accounts")
        return

    prepared = prepare_from_tsv_rows(rows)

    print("[INFO] Domains found (from TSV):")
    for d in prepared["domains"]:
        print("  -", d)

    # Optionally test a subset:
    # domains_to_process = ["podbeez.com"]
    domains_to_process = None

    server = ServerConfig(
        host=host,
        cli_port=cli_port,
        username=username,
        password=password,
        cli_timeout=8.0,
    )

    print("\n[INFO] Processing server domains in parallel...\n")
    report = process_server_domains(
        server=server,
        prepared=prepared,
        max_workers=max_workers,
        domains=domains_to_process,
    )

    # ---- Print summary ----
    print("\n========== SERVER REPORT ==========")
    print("Server:", report["server"])
    print("Domains:", report["total_domains"])
    print("SUCCESS:", report["success"])
    print("PARTIAL:", report["partial"])
    print("FAILED :", report["failed"])
    print("Duration (s):", report["duration_s"])
    print("===================================\n")

    # ---- Print per-domain results (compact) ----
    for r in report["results"]:
        domain = r.get("domain")
        status = r.get("status")
        dur = r.get("duration_s")
        acc_count = len(r.get("accounts") or [])
        err_count = len(r.get("errors") or [])
        print(f"{domain:25}  {status:8}  accounts={acc_count:<4} errors={err_count:<3} dur={dur}")

    # Uncomment to print full details:
    # print("\n[DEBUG] Full report:")
    pprint(report, width=140)


if __name__ == "__main__":
    asyncio.run(main())
