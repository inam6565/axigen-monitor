# axigen_cli/quotas.py

from __future__ import annotations

from typing import Dict, Tuple
from .client import AxigenCLIClient


def parse_quota_show(raw: str) -> Dict[str, str]:
    """
    Parse the output of 'CONFIG quotas' -> 'SHOW' for an account.

    Typical lines look like:
        totalMessageSize = 2097152 [explicit, overrides inherited value: 1048576]
        totalMessageCount = 1000 [explicit]

    We:
    - skip empty / irrelevant lines
    - keep key and the main value (3rd token after 'key = value')
    """
    quotas: Dict[str, str] = {}

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue

        # Skip obvious non-data lines; tweak these if needed:
        lower = line.lower()
        if lower.startswith("general parameters"):
            continue
        if lower.startswith("inherited from"):
            continue
        if lower.startswith("using defaults"):
            continue

        if "=" not in line:
            continue

        parts = line.split()
        # expecting: key = value ...
        if len(parts) >= 3 and parts[1] == "=":
            key = parts[0]
            value = parts[2]
            quotas[key] = value

    return quotas


def get_account_quota(
    host: str,
    port: int,
    username: str,
    password: str,
    domain: str,
    account: str,
) -> Tuple[Dict[str, str], str]:
    """
    Connect to Axigen CLI and return the assigned quotas for a single account.

    - `account` may be either local part ("inam") or full email ("inam@podbeez.com")
    - Returns (quotas_dict, raw_output_from_show)

    Example quotas_dict:
        {
            "totalMessageSize": "2097152",
            "totalMessageCount": "1000",
            ...
        }
    """
    # Extract local part (e.g. "inam" from "inam@podbeez.com")
    local_part = account.split("@", 1)[0]

    with AxigenCLIClient(host, port) as cli:
        cli.login(username, password)

        # Go to the domain
        resp = cli.run_command(f"UPDATE domain name {domain}")
        if "-ERR" in resp:
            raise RuntimeError(f"UPDATE domain failed: {resp}")

        # Go to the account (local part only)
        resp = cli.run_command(f"UPDATE account name {local_part}")
        if "-ERR" in resp:
            raise RuntimeError(
                f'UPDATE account failed for "{local_part}" in domain "{domain}": {resp}'
            )

        # Enter quotas context
        resp = cli.run_command("CONFIG quotas")
        if "-ERR" in resp:
            raise RuntimeError(f"CONFIG quotas failed: {resp}")

        # Show assigned quotas
        raw_show = cli.run_command("SHOW")

    quotas = parse_quota_show(raw_show)
    return quotas, raw_show
