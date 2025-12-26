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

    def is_error(resp: str) -> bool:
        r = (resp or "").lower()
        return ("-err" in r) or ("error" in r) or ("unknown" in r)

    with AxigenCLIClient(host, port) as cli:
        cli.login(username, password)

        cmd1 = f"UPDATE domain name {domain}"
        resp1 = cli.run_command(cmd1)
        print(f"[DEBUG][QUOTA] {account} cmd={cmd1} resp={repr(resp1)}")
        if is_error(resp1):
            raise RuntimeError(f"UPDATE domain failed: {resp1}")

        cmd2 = f"UPDATE account name {local_part}"
        resp2 = cli.run_command(cmd2)
        print(f"[DEBUG][QUOTA] {account} cmd={cmd2} resp={repr(resp2)}")
        if is_error(resp2):
            raise RuntimeError(f'UPDATE account failed for "{local_part}" in "{domain}": {resp2}')

        cmd3 = "CONFIG quotas"
        resp3 = cli.run_command(cmd3)
        print(f"[DEBUG][QUOTA] {account} cmd={cmd3} resp={repr(resp3)}")
        if is_error(resp3):
            raise RuntimeError(f"CONFIG quotas failed: {resp3}")

        cmd4 = "SHOW"
        raw_show = cli.run_command(cmd4)
        print(f"[DEBUG][QUOTA] {account} cmd={cmd4} raw_show_len={len(raw_show or '')} raw_show={repr(raw_show[:200])}")

    quotas = parse_quota_show(raw_show or "")
    return quotas, raw_show or ""