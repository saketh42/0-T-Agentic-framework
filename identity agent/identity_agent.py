# identity_agent.py

from registry import get_agent
from validator import validate_request
from context_builder import build_context


def resolve_identity(request):

    print("\n==============================")
    print("Identity Agent Processing Start")
    print("==============================")

    print("[IdentityAgent] Step 1: Validate Request")
    validate_request(request)

    print("[IdentityAgent] Step 2: Resolve Agent Identity")
    print("[IdentityAgent] Agent ID:", request.agent_id)

    agent_data = get_agent(request.agent_id)

    if not agent_data:
        print("[IdentityAgent] ERROR: Unknown agent")
        raise Exception("UNKNOWN_AGENT")

    print("[IdentityAgent] Step 3: Check Agent Status")

    if agent_data["status"] != "active":
        print("[IdentityAgent] Agent status:", agent_data["status"])
        print("[IdentityAgent] Access denied due to suspended agent")
        raise Exception("AGENT_SUSPENDED")

    print("[IdentityAgent] Agent status: active")

    print("[IdentityAgent] Step 4: Retrieve Agent Metadata")

    print("    Role:", agent_data["role"])
    print("    Risk Tier:", agent_data["risk_tier"])
    print("    Autonomy:", agent_data["autonomy_level"])
    print("    Owner:", agent_data["owner"])

    print("[IdentityAgent] Step 5: Building Decision Context")

    context = build_context(
        request.agent_id,
        agent_data,
        request.session_id,
        request.environment
    )

    print("[IdentityAgent] Identity resolution complete")

    return context