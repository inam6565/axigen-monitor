# axigen_cli/controller.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


@dataclass(frozen=True)
class ServerConfig:
    host: str
    cli_port: int
    username: str
    password: str
    cli_timeout: float = 8.0


def process_server_domains(
    server: ServerConfig,
    prepared: Dict[str, Any],
    max_workers: int = 10,
    domains: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Controller: processes one server (active TSV-visible domains) using a thread pool.

    Inputs:
      server: CLI creds
      prepared: output of prepare_from_tsv_rows()
      max_workers: number of concurrent domain workers
      domains: optional subset list to process (defaults to prepared['domains'])

    Returns:
      {
        "server": {"host":..., "cli_port":..., "username":...},
        "total_domains": int,
        "success": int,
        "partial": int,
        "failed": int,
        "duration_s": float,
        "results": [DomainResult, ...]
      }
    """
    from axigen_cli.worker import process_domain  # import here to avoid circulars

    start = time.time()

    accounts_by_domain: Dict[str, List[str]] = prepared["accounts_by_domain"]
    usage_by_email_kb: Dict[str, int] = prepared["usage_by_email_kb"]

    domain_list = domains if domains is not None else prepared.get("domains", [])
    domain_list = [d.strip().lower() for d in domain_list if d and d.strip()]
    domain_list = sorted(set(domain_list))

    results: List[Dict[str, Any]] = []

    if not domain_list:
        return {
            "server": {"host": server.host, "cli_port": server.cli_port, "username": server.username},
            "total_domains": 0,
            "success": 0,
            "partial": 0,
            "failed": 0,
            "duration_s": round(time.time() - start, 3),
            "results": [],
        }

    # Keep workers reasonable vs. domain count
    worker_count = max(1, min(int(max_workers), len(domain_list)))

    # Submit all domain jobs
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

        # Collect as they finish
        for fut in as_completed(future_map):
            domain = future_map[fut]
            try:
                res = fut.result()
            except Exception as e:
                # If process_domain throws unexpectedly, wrap it
                res = {
                    "domain": domain,
                    "status": "FAILED",
                    "accounts": [],
                    "errors": [{"email": None, "stage": "controller_exception", "error": repr(e)}],
                    "duration_s": None,
                }
            results.append(res)

    # Summaries
    success = sum(1 for r in results if r.get("status") == "SUCCESS")
    partial = sum(1 for r in results if r.get("status") == "PARTIAL")
    failed = sum(1 for r in results if r.get("status") == "FAILED")

    return {
        "server": {"host": server.host, "cli_port": server.cli_port, "username": server.username},
        "total_domains": len(domain_list),
        "success": success,
        "partial": partial,
        "failed": failed,
        "duration_s": round(time.time() - start, 3),
        "results": sorted(results, key=lambda x: (x.get("domain") or "")),
    }
