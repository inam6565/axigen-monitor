import asyncio
import getpass
from .tsv import _fetch_webadmin_accounts
from .tsv import prepare_from_tsv_rows

async def run_fetch():
    host = input("Host: ").strip()
    port = int(input("Port: ").strip())
    user = input("Username: ").strip()
    password = getpass.getpass("Password: ")

    print("\n[INFO] Fetching accounts...\n")

    rows = await _fetch_webadmin_accounts(
        host=host,
        port=port,
        user=user,
        password=password,
    )

    if rows is None:
        print("[ERROR] Failed to fetch accounts")
        return

    print(f"[SUCCESS] Retrieved {len(rows)} accounts\n")
    print(prepare_from_tsv_rows(rows))
    # Pretty-print rows
    


if __name__ == "__main__":
    asyncio.run(run_fetch())