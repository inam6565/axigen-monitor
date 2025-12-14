from __future__ import annotations
import re
from typing import List, Dict, Optional
import requests
import urllib3
from io import StringIO
import csv


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# local part: letters, digits, dot, underscore, hyphen
LOCAL_PART_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$")



def parse_account_list(raw: str) -> List[str]:
    accounts: List[str] = []

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue

        lower = line.lower()

        if "accounts" in lower:
            continue
        if line.startswith("---") or line.startswith("==="):
            continue
        if line.startswith("+OK") or line.startswith("-ERR"):
            continue

        parts = line.split()
        if not parts:
            continue

        candidate = parts[0]
        cand_lower = candidate.lower()

        if cand_lower in {"name", "account", "accounts", "status"}:
            continue

        if candidate.startswith("<") and candidate.endswith(">"):
            continue
        if any(ch in candidate for ch in ("@", ":", "#", "<", ">", "|")):
            continue
        if candidate.startswith("+") or candidate.startswith("-"):
            continue

        if not LOCAL_PART_RE.match(candidate):
            continue

        accounts.append(candidate)

    seen = set()
    unique_accounts: List[str] = []
    for acc in accounts:
        if acc not in seen:
            seen.add(acc)
            unique_accounts.append(acc)

    return unique_accounts


# ------------------------------
# Parse TSV from WebAdmin
# ------------------------------
def _parse_tsv_accounts(tsv_text: str) -> List[Dict]:
    """
    Parse TSV returned by /data/accounts.
    Each row becomes a dict with keys from the header row.
    """
    reader = csv.DictReader(StringIO(tsv_text), delimiter="\t")
    return [row for row in reader]



from typing import Dict, List, Any, Tuple
from collections import defaultdict

def prepare_from_tsv_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convert WebAdmin TSV rows into worker-ready structures.
    No HTTP calls. Pure transformation.

    Returns:
      {
        "domains": [ "podbeez.com", ... ],
        "accounts_by_domain": { "podbeez.com": ["test@podbeez.com", ...], ... },
        "usage_by_email_kb": { "test@podbeez.com": 2432, ... },
        "usage_by_domain_kb": { "podbeez.com": 4863, ... },  # optional summary
      }
    """
    usage_by_email_kb: Dict[str, int] = {}
    accounts_by_domain: Dict[str, List[str]] = defaultdict(list)
    usage_by_domain_kb: Dict[str, int] = defaultdict(int)

    for row in rows:
        # remove junk key that comes from DictReader occasionally
        if None in row:
            row = dict(row)
            row.pop(None, None)

        email = (row.get("accountEmail") or "").strip().lower()
        if not email or "@" not in email:
            continue

        # parse used KB safely
        raw_kb = row.get("mboxSizeKb", 0)
        try:
            used_kb = int(raw_kb or 0)
        except (ValueError, TypeError):
            used_kb = 0

        domain = email.split("@", 1)[1]

        usage_by_email_kb[email] = used_kb
        accounts_by_domain[domain].append(email)
        usage_by_domain_kb[domain] += used_kb

    domains = sorted(accounts_by_domain.keys())

    return {
        "domains": domains,
        "accounts_by_domain": dict(accounts_by_domain),
        "usage_by_email_kb": usage_by_email_kb,
        "usage_by_domain_kb": dict(usage_by_domain_kb),
    }


async def _fetch_webadmin_accounts(host: str, port: int, user: str, password: str) -> Optional[List[Dict]]:
    urls = [
        f"https://{host}:{port}/data/accounts",  # HTTPS first (Ace is HTTPS-only)
        f"http://{host}:{port}/data/accounts",   # HTTP fallback (Podbeez is HTTP)
    ]

    for url in urls:
        try:
            
            resp = requests.get(
                url,
                auth=(user, password),
                verify=False,   # allow expired/self-signed certs (Ace)
                timeout=8,
                headers={"Connection": "close"},  # helps with some servers
            )
            print("[DEBUG] status:", resp.status_code)

            if resp.status_code != 200:
                continue

            rows = _parse_tsv_accounts(resp.text)
            print("[DEBUG] parsed rows:", len(rows))
            if rows:
                return rows

        except Exception as e:
            print("[DEBUG] webadmin fetch exception:", repr(e))
            continue

    return None