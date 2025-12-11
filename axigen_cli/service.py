# axigen_cli/service.py

from __future__ import annotations
from typing import List, Dict, Tuple
from .domains import list_domains
from .accounts import list_accounts_for_domain
from .qoutas import get_account_quota



def get_domains_summary(
    host: str,
    port: int,
    username: str,
    password: str,
) -> Tuple[List[Dict[str, object]], int, int]:
    """
    Returns:
      - list of dicts: [{ "domain": str, "account_count": int }, ...]
      - total number of domains
      - total number of accounts (across all domains)
    """
    domains = list_domains(host=host, port=port, username=username, password=password)

    summary: List[Dict[str, object]] = []
    total_accounts = 0

    for domain in domains:
        accounts = list_accounts_for_domain(
            host=host,
            port=port,
            username=username,
            password=password,
            domain=domain,
        )
        count = len(accounts)
        total_accounts += count
        summary.append({"domain": domain, "account_count": count})

    total_domains = len(domains)
    return summary, total_domains, total_accounts


def get_domain_accounts(
    host: str,
    port: int,
    username: str,
    password: str,
    domain: str,
) -> List[Dict]:
    """
    Returns list of accounts for a single domain with quotas.
    Each account is a dict:
      {
        "email": str
        "used_mb": int
      }
    """
    return list_accounts_for_domain(
        host=host,
        port=port,
        username=username,
        password=password,
        domain=domain,
    )

def get_qoutas(
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
    return get_account_quota(
    host=host,
    port=port,
    username=username,
    password=password,
    domain=domain,
    account=account,
    )