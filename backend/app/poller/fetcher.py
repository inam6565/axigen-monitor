from axigen_cli.domains import list_domains
from axigen_cli.accounts import list_accounts_for_domain
from app.utils.encrypt import decrypt_password


def fetch_domains(server):
    """Fetch domains from Axigen server"""
    password = decrypt_password(server.password_enc)

    return list_domains(
        host=server.hostname,
        port=server.cli_port,
        username=server.username,
        password=password,
    )


def fetch_domain_accounts(server, domain):
    """Fetch accounts + quota for one domain"""
    password = decrypt_password(server.password_enc)

    return list_accounts_for_domain(
        host=server.hostname,
        port=server.cli_port,
        username=server.username,
        password=password,
        domain=domain,
        webadmin_port=server.webadmin_port,
    )
