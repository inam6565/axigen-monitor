import asyncio
from backend.app.poller.poller_v3 import poll_servers_v3

job_id = "b9afa665-faf0-41af-b66a-3df4470587ce"  # from /jobs/run response

asyncio.run(poll_servers_v3(job_id=job_id))