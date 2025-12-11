# axigen_cli/domains.py

from __future__ import annotations

from typing import List
from .client import AxigenCLIClient


def parse_domain_list(raw: str) -> List[str]:
    """
    Very simple parser for 'LIST domains' output.

    Axigen's CLI LIST command returns tables; we:
    - skip empty lines and header/underline lines
    - take the first column of each data line as the domain
    You may need to tweak this based on what your server prints.
    """
    domains: List[str] = []

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # skip header-ish lines
        if line.lower().startswith("list") or line.lower().startswith("domains"):
            continue
        if line.startswith("---") or line.startswith("==="):
            continue

        parts = line.split()
        if not parts:
            continue

        # heuristic: first column is usually the domain name
        candidate = parts[0]
        # very basic filter (adjust if you use weird domain names)
        if "." in candidate:
            domains.append(candidate)

    # de-duplicate while preserving order
    seen = set()
    unique_domains: List[str] = []
    for d in domains:
        if d not in seen:
            seen.add(d)
            unique_domains.append(d)
    print(unique_domains)
    return unique_domains


def list_domains(
    host: str,
    port: int,
    username: str,
    password: str,
) -> List[str]:
    """
    Connect to Axigen CLI and return list of domains.
    """
    with AxigenCLIClient(host, port) as cli:
        cli.login(username, password)
        raw = cli.run_command("LIST domains")
        return parse_domain_list(raw)
