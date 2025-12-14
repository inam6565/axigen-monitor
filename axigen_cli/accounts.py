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
            if email.lower() == "test5@abdullah12.com":
                print("\n[DEBUG][TEST5] quotas dict:", quotas)
                print("[DEBUG][TEST5] raw quota output:\n", _raw, "\n")
            if total_msg_size_kb is None:
                print(f"[DEBUG][QUOTA] totalMessageSize missing for {email} domain={domain}. quotas keys={list(quotas.keys())}")
                # optional: print raw response if you have it
                # print(f"[DEBUG][QUOTA_RAW] {email} -> {_raw}")
                assigned_mb = None
            else:
                assigned_mb = _size_kb_to_gb(total_msg_size_kb)
        except Exception as e:
            print(f"[DEBUG][QUOTA_ERR] {email} domain={domain} -> {repr(e)}")
            # if quota retrieval fails for this account, just leave assigned_mb as None
            assigned_mb = None

        # ----- Used size from WebAdmin TSV -----
        if tsv_accounts:
            for record in tsv_accounts:
                if (record.get("accountEmail") or "").strip().lower() == email.lower():
                    raw_mb = _size_kb_to_mb(record.get("mboxSizeKb"))

                    # STANDARD:
                    # - None if missing or 0
                    # - int MB if > 0
                    used_mb = None if (raw_mb is None or raw_mb == 0) else raw_mb
                    break

        results.append({
            "email": email,
            "assigned_mb": assigned_mb,
            "used_mb": used_mb,
        })
    print(results)
    return results
