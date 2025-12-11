# axigen_cli/accounts.py

from __future__ import annotations
import re
from typing import List, Dict, Optional
import requests
import urllib3
from io import StringIO
import csv

from .client import AxigenCLIClient, AxigenCLIError
from .qoutas import get_account_quota  # <-- NEW IMPORT

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# local part: letters, digits, dot, underscore, hyphen
LOCAL_PART_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$")


# ------------------------------
# Parse "LIST Accounts" Result
# ------------------------------
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


# ------------------------------
# Convert size to MB
# ------------------------------
def _size_kb_to_mb(kb_value) -> Optional[int]:
    try:
        return int(kb_value) // 1024
    except (TypeError, ValueError):
        return None

# ------------------------------
# Convert size to GB
# ------------------------------
def _size_kb_to_gb(kb_value) -> Optional[int]:
    try:
        return int(kb_value) // (1024*1024)
    except (TypeError, ValueError):
        return None

# ------------------------------
# Fetch WebAdmin TSV
# ------------------------------
def _fetch_webadmin_accounts(host: str, port: int, user: str, password: str) -> Optional[List[Dict]]:
    url = f"https://{host}:{port}/data/accounts"
    try:
        resp = requests.get(url, auth=(user, password), verify=False, timeout=5)
        if resp.status_code != 200:
            return None
        return _parse_tsv_accounts(resp.text)
    except Exception:
        return None


# ------------------------------
# Main Function
# ------------------------------
def list_accounts_for_domain(
    host: str,
    port: int,
    username: str,
    password: str,
    domain: str,
    webadmin_port: int = 9000,
) -> List[Dict]:
    """
    Returns list of accounts with quotas:
        [
          {
            "email": "user@domain",
            "assigned_mb": 1024,   # from totalMessageSize quota (in KB -> MB)
            "used_mb": 800         # from WebAdmin TSV (mboxSizeKb -> MB)
          }
        ]
    """

    # -------- CLI: get account list (local parts) --------
    with AxigenCLIClient(host, port) as cli:
        cli.login(username, password)

        resp = cli.run_command(f"UPDATE Domain {domain}")
        if "unknown" in resp.lower() or "error" in resp.lower():
            raise AxigenCLIError(f"Could not enter domain context for {domain}: {resp.strip()}")

        raw_accounts = cli.run_command("LIST Accounts")

        try:
            cli.run_command("BACK")
        except AxigenCLIError:
            pass

        local_parts = parse_account_list(raw_accounts)

    full_emails = [f"{lp}@{domain}" for lp in local_parts]

    # -------- WEBADMIN: fetch TSV once --------
    tsv_accounts = _fetch_webadmin_accounts(host, webadmin_port, username, password)

    results = []

    for email in full_emails:
        assigned_mb: Optional[int] = None
        used_mb: Optional[int] = None

        # ----- Quotas via CLI (totalMessageSize) -----
        # totalMessageSize in Axigen quotas is in KB, so we reuse _size_kb_to_mb.
        try:
            quotas, _raw = get_account_quota(
                host=host,
                port=port,
                username=username,
                password=password,
                domain=domain,
                account=email,  # full email is accepted; function extracts local part
            )
            total_msg_size_kb = quotas.get("totalMessageSize")
            if total_msg_size_kb is not None:
                assigned_mb = _size_kb_to_gb(total_msg_size_kb)
        except Exception:
            # if quota retrieval fails for this account, just leave assigned_mb as None
            assigned_mb = None

        # ----- Used size from WebAdmin TSV -----
        if tsv_accounts:
            for record in tsv_accounts:
                if record.get("accountEmail", "").lower() == email.lower():
                    raw_mb = _size_kb_to_mb(record.get("mboxSizeKb"))
                    if raw_mb is not None:
                        if raw_mb < 1024:
                            used_mb = f"{raw_mb} MB"
                        else:
                            used_gb = raw_mb / 1024
                            used_mb = f"{used_gb:.2f} GB"
                    else:
                        used_mb = None
                    #used_mb = _size_kb_to_mb(record.get("mboxSizeKb"))
                    break

        results.append({
            "email": email,
            "assigned_mb": assigned_mb,
            "used_mb": used_mb,
        })
    print(results)
    return results
