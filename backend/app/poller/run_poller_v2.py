import asyncio
from backend.app.poller.poller_v2 import poll_servers_v2

if __name__ == "__main__":
    asyncio.run(poll_servers_v2(max_workers_per_server=10))
