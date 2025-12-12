import argparse
import asyncio
from getpass import getpass
from backend.app.db.base import AsyncSessionLocal
from backend.app.db.models import Server
from backend.app.utils.encrypt import encrypt_password


async def add_server(name, hostname, cli_port, webadmin_port, username, password):
    async with AsyncSessionLocal() as db:
        encrypted = encrypt_password(password)

        server = Server(
            name=name,
            hostname=hostname,
            cli_port=cli_port,
            webadmin_port=webadmin_port,
            username=username,
            encrypted_password=encrypted,
        )

        db.add(server)
        await db.commit()
        print(f"[OK] Server added: {name}")


def parse_args():
    parser = argparse.ArgumentParser(description="Add a server to DB (interactive supported)")

    parser.add_argument("--name", help="Server name")
    parser.add_argument("--hostname", help="Hostname or IP")
    parser.add_argument("--cli_port", type=int, help="CLI port")
    parser.add_argument("--webadmin_port", type=int, help="WebAdmin port")
    parser.add_argument("--username", help="Username")
    parser.add_argument("--password", help="Password")

    return parser.parse_args()


def ensure_values(args):
    # Ask for missing values
    if not args.name:
        args.name = input("Enter server name: ")

    if not args.hostname:
        args.hostname = input("Enter hostname: ")

    if not args.cli_port:
        args.cli_port = int(input("Enter CLI port: "))

    if not args.webadmin_port:
        args.webadmin_port = int(input("Enter WebAdmin port: "))

    if not args.username:
        args.username = input("Enter username: ")

    if not args.password:
        args.password = getpass("Enter password: ")  # hidden input

    return args


if __name__ == "__main__":
    args = parse_args()
    args = ensure_values(args)

    asyncio.run(add_server(
        args.name,
        args.hostname,
        args.cli_port,
        args.webadmin_port,
        args.username,
        args.password
    ))
