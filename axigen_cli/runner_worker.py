import asyncio
import getpass
from pprint import pprint

from axigen_cli.tsv import _fetch_webadmin_accounts, prepare_from_tsv_rows
from axigen_cli.worker import process_domain


async def main():
    # ---- Axigen CLI credentials ----
    host = input("Axigen host: ").strip()
    port = int(input("Axigen port [7000]: ").strip() or "7000")
    username = input("Axigen username: ").strip()
    password = getpass.getpass("Axigen password: ")

    # ---- WebAdmin credentials ----
    wa_port = int(input("WebAdmin port: ").strip())
    

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

    print("[INFO] Domains found:")
    for d in prepared["domains"]:
        print("  -", d)

    domain = input("\nEnter domain to test: ").strip().lower()
    if domain not in prepared["domains"]:
        print(f"[ERROR] Domain '{domain}' not found in TSV data")
        return

    print(f"\n[INFO] Processing domain: {domain}\n")

    result = process_domain(
        host=host,
        port=port,
        username=username,
        password=password,
        domain=domain,
        accounts_by_domain=prepared["accounts_by_domain"],
        usage_by_email_kb=prepared["usage_by_email_kb"],
        cli_timeout=8.0,
    )

    print("\n[RESULT]")
    pprint(result, width=120)


if __name__ == "__main__":
    asyncio.run(main())
