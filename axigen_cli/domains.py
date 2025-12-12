# axigen_cli/domains.py

from __future__ import annotations
from typing import List, Dict
from .client import AxigenCLIClient


def parse_all_domains(raw: str) -> List[Dict[str, str]]:
    """
    Parser for 'LIST AllDomains'.
    Expected columns:
        name    Status
    Example:
        haseeb.co     enabled
        inam.org      disabled
    """
    domains = []

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue

        # Skip headers / separators / footer lines
        lower = line.lower()
        if lower.startswith("the list of") or lower.startswith("name") or lower.startswith("list"):
            continue
        if line.startswith("---") or line.startswith("==="):
            continue
        if line.startswith("+OK") or line.startswith("-ERR"):
            continue

        parts = line.split()
        if len(parts) < 2:
            continue

        domain_name = parts[0]
        status = parts[-1].lower()  # enabled / disabled / locked etc.

        # Basic validation
        if "." not in domain_name:
            continue

        domains.append({"domain": domain_name, "status": status})

    return domains


def list_all_domains(
    host: str,
    port: int,
    username: str,
    password: str,
) -> List[Dict[str, str]]:
    """
    Calls `LIST AllDomains` and returns:
        [
            { "domain": "example.com", "status": "enabled" },
            { "domain": "old.org", "status": "disabled" }
        ]
    """
    with AxigenCLIClient(host, port) as cli:
        cli.login(username, password)
        raw = cli.run_command("LIST AllDomains")
        return parse_all_domains(raw)
