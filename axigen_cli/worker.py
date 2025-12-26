from typing import Dict, Any, List, Optional, Tuple
import time
from .client import AxigenCLIClient
from .qoutas import parse_quota_show
# expects you already have:
# - AxigenCLIClient
# - parse_quota_show(raw: str) -> Dict[str, str]

def process_domain(
    host: str,
    port: int,
    username: str,
    password: str,
    domain: str,
    accounts_by_domain: Dict[str, List[str]],
    usage_by_email_kb: Dict[str, int],
    cli_timeout: float = 8.0,
) -> Dict[str, Any]:
    """
    Process one domain end-to-end using ONE CLI connection.

    Returns:
      {
        "domain": str,
        "status": "SUCCESS" | "PARTIAL" | "FAILED",
        "accounts": [
           {"email": str, "assigned_mb": Optional[int], "used_mb": int}
        ],
        "errors": [ {"email": Optional[str], "stage": str, "error": str} ],
        "duration_s": float
      }
    """
    start = time.time()
    errors: List[Dict[str, Any]] = []
    results: List[Dict[str, Any]] = []

    emails = accounts_by_domain.get(domain, [])
    if not emails:
        return {
            "domain": domain,
            "status": "SUCCESS",   # nothing to do; treat as success
            "accounts": [],
            "errors": [],
            "duration_s": round(time.time() - start, 3),
        }

    def is_error(resp: str) -> bool:
        r = (resp or "").lower()
        # keep it broad; Axigen errors vary
        return ("-err" in r) or ("error" in r) or ("unknown" in r) or ("failed" in r)

    def kb_to_mb_floor(kb: int) -> int:
        return int(kb) // 1024 if kb and kb > 0 else 0

    def parse_assigned_mb(quotas: Dict[str, str]) -> Optional[int]:
        # Axigen typically uses totalMessageSize in KB
        raw = quotas.get("totalMessageSize")
        if raw is None:
            return None  # treat as "unlimited / not explicitly set"
        try:
            kb = int(raw)
        except (ValueError, TypeError):
            return None
        if kb <= 0:
            return None
        return kb_to_mb_floor(kb)

    # ---- CLI session ----
    try:
        with AxigenCLIClient(host, port, timeout=cli_timeout) as cli:
            cli.login(username, password)

            # 1) set domain context
            cmd = f"UPDATE domain name {domain}"
            resp = cli.run_command(cmd)
            if is_error(resp):
                return {
                    "domain": domain,
                    "status": "FAILED",
                    "accounts": [],
                    "errors": [{"email": None, "stage": "update_domain", "error": resp.strip()}],
                    "duration_s": round(time.time() - start, 3),
                }

            # 2) iterate accounts (sequential)
            domain_had_account_errors = False

            for email in emails:
                email_norm = (email or "").strip().lower()
                if "@" not in email_norm:
                    domain_had_account_errors = True
                    errors.append({"email": email, "stage": "validate_email", "error": "invalid email"})
                    continue

                local_part = email_norm.split("@", 1)[0]

                # used quota from TSV (KB -> MB)
                used_kb = int(usage_by_email_kb.get(email_norm, 0) or 0)
                used_mb = kb_to_mb_floor(used_kb)

                try:
                    # account context
                    cmd2 = f"UPDATE account name {local_part}"
                    resp2 = cli.run_command(cmd2)
                    if is_error(resp2):
                        domain_had_account_errors = True
                        errors.append({"email": email_norm, "stage": "update_account", "error": resp2.strip()})
                        # still return used_mb info if you want:
                        results.append({"email": email_norm, "assigned_mb": None, "used_mb": used_mb})
                        continue

                    # quotas config + show
                    resp3 = cli.run_command("CONFIG quotas")
                    if is_error(resp3):
                        domain_had_account_errors = True
                        errors.append({"email": email_norm, "stage": "config_quotas", "error": resp3.strip()})
                        results.append({"email": email_norm, "assigned_mb": None, "used_mb": used_mb})
                        continue

                    raw_show = cli.run_command("SHOW")
                    cli.run_command("BACK")
                    cli.run_command("BACK")
                    if is_error(raw_show):
                        domain_had_account_errors = True
                        errors.append({"email": email_norm, "stage": "show_quotas", "error": raw_show.strip()})
                        results.append({"email": email_norm, "assigned_mb": None, "used_mb": used_mb})
                        continue

                    quotas = parse_quota_show(raw_show or "")
                    assigned_mb = parse_assigned_mb(quotas)

                    results.append({
                        "email": email_norm,
                        "assigned_mb": assigned_mb,
                        "used_mb": used_mb,
                    })

                except Exception as e:
                    domain_had_account_errors = True
                    errors.append({"email": email_norm, "stage": "exception", "error": repr(e)})
                    results.append({"email": email_norm, "assigned_mb": None, "used_mb": used_mb})

        status = "PARTIAL" if errors else "SUCCESS"
        return {
            "domain": domain,
            "status": status,
            "accounts": results,
            "errors": errors,
            "duration_s": round(time.time() - start, 3),
        }

    except Exception as e:
        # connection/login-level failure
        return {
            "domain": domain,
            "status": "FAILED",
            "accounts": [],
            "errors": [{"email": None, "stage": "cli_session", "error": repr(e)}],
            "duration_s": round(time.time() - start, 3),
        }
