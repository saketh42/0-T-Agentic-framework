from pathlib import Path
import sys


IDENTITY_SRC_PATH = Path(__file__).resolve().parents[3] / "identity agent" / "src"
if str(IDENTITY_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(IDENTITY_SRC_PATH))

from identity_agent import resolve_identity  # noqa: E402
from models import IdentityRequest  # noqa: E402


def resolve_gateway_identity(payload):
    request = IdentityRequest(
        agent_id=payload.agent_id,
        session_id=payload.session_id,
        environment=payload.environment,
        tenant_id=payload.tenant_id,
        origin=payload.origin,
        network_zone=payload.network_zone
    )

    result = resolve_identity(request)
    return result.to_dict()
