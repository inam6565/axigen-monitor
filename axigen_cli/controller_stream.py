# axigen_cli/controller_stream.py
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Dict, Any, List, Optional
import time

from axigen_cli.controller import ServerConfig


def process_server_domains_stream(
    server: ServerConfig,
    prepared: Dict[str, Any],
    on_result: Callable[[Dict[str, Any]], None],
    max_workers: int = 10,
    domains: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Stream domain results to `on_result(result)` as soon as each domain completes.
    Returns a summary report dict.
    """
    from axigen_cli.worker import process_domain  # your existing domain worker

    start = time.time()

    accounts_by_domain: Dict[str, List[str]] = prepared["accounts_by_domain"]
    usage_by_email_kb: Dict[str, int] = prepared["usage_by_email_kb"]

    domain_list = domains if domains is not None else prepared.get("domains", [])
    domain_list = [d.strip().lower() for d in domain_list if d and d.strip()]
    domain_list = sorted(set(domain_list))

    if not domain_list:
        return {
            "server": {"host": server.host, "cli_port": server.cli_port, "username": server.username},
            "total_domains": 0,
            "success": 0,
            "partial": 0,
            "failed": 0,
            "duration_s": round(time.time() - start, 3),
        }

    worker_count = max(1, min(int(max_workers), len(domain_list)))

    success = partial = failed = 0

    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        future_map = {}
        for domain in domain_list:
            fut = pool.submit(
                process_domain,
                server.host,
                server.cli_port,
                server.username,
                server.password,
                domain,
                accounts_by_domain,
                usage_by_email_kb,
                server.cli_timeout,
            )
            future_map[fut] = domain

        for fut in as_completed(future_map):
            domain = future_map[fut]
            try:
                res = fut.result()
            except Exception as e:
                res = {
                    "domain": domain,
                    "status": "FAILED",
                    "accounts": [],
                    "errors": [{"email": None, "stage": "controller_exception", "error": repr(e)}],
                    "duration_s": None,
                }

            st = res.get("status")
            if st == "SUCCESS":
                success += 1
            elif st == "PARTIAL":
                partial += 1
            else:
                failed += 1

            on_result(res)

    return {
        "server": {"host": server.host, "cli_port": server.cli_port, "username": server.username},
        "total_domains": len(domain_list),
        "success": success,
        "partial": partial,
        "failed": failed,
        "duration_s": round(time.time() - start, 3),
    }
