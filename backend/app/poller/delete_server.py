import argparse
import asyncio

from sqlalchemy import delete
from backend.app.db.base import AsyncSessionLocal
from backend.app.db.models import Server


async def delete_server(hostname: str):
    async with AsyncSessionLocal() as db:
        stmt = delete(Server).where(Server.hostname == hostname)
        result = await db.execute(stmt)
        await db.commit()

        # result.rowcount may be None on some DBs, so handle that safely
        deleted = result.rowcount if result.rowcount is not None else 0

        if deleted == 0:
            print(f"[WARN] No server found with hostname: {hostname}")
        else:
            print(f"[OK] Deleted {deleted} server(s) with hostname: {hostname}")


def parse_args():
    parser = argparse.ArgumentParser(description="Delete server(s) by hostname")
    parser.add_argument("--hostname", help="Hostname of the server to delete")
    return parser.parse_args()


def ensure_values(args):
    if not args.hostname:
        args.hostname = input("Enter hostname of server to delete: ").strip()
    return args


if __name__ == "__main__":
    args = parse_args()
    args = ensure_values(args)

    asyncio.run(delete_server(args.hostname))
