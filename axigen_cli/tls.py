# axigen_cli/tls.py
from enum import Enum
from typing import Optional, Union

class TLSMode(str, Enum):
    STRICT = "strict"        # verify certs
    INSECURE = "insecure"    # allow bad certs
    DISABLED = "disabled"    # HTTP only

def resolve_verify(
    tls_mode: TLSMode,
    ca_bundle: Optional[str] = None,
) -> Union[bool, str, None]:
    """
    Return value suitable for requests.verify
    """
    if tls_mode == TLSMode.STRICT:
        return ca_bundle if ca_bundle else True

    if tls_mode == TLSMode.INSECURE:
        return ca_bundle if ca_bundle else False

    # DISABLED → HTTP, requests.verify not applicable
    return None
