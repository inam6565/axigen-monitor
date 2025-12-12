import asyncio
from backend.app.poller.poller import poll_servers

if __name__ == "__main__":
    asyncio.run(poll_servers())
