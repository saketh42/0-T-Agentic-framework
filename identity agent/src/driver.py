# driver.py

from models import IdentityRequest
from identity_agent import resolve_identity


def simulate_agent(agent_id):

    print("\n===========================================")
    print("Simulation Case: ", agent_id)
    print("===========================================")

    request = IdentityRequest(
        agent_id=agent_id,
        session_id="SESSION-1001",
        environment="production",
        tenant_id="tenant-acme",
        origin="soc-copilot-ui",
        network_zone="internal"
    )

    print("\n[Driver] Generated Request")
    print(vars(request))

    result = resolve_identity(request)

    if result.decision == "allow":
        print("\n[Driver] Identity Resolution SUCCESS")
        print("[Driver] Identity Decision:")
        print(result.to_dict())
        return

    print("\n[Driver] Identity Resolution FAILED")

    if result.reason == "UNKNOWN_AGENT":
        print("[Driver] Reason: Agent not registered")
    elif result.reason == "AGENT_SUSPENDED":
        print("[Driver] Reason: Agent suspended / blocked")
    else:
        print("[Driver] Error:", result.reason)

    print("[Driver] Identity Decision:")
    print(result.to_dict())


def run_simulation():

    print("\n===================================")
    print("Agent Identity Resolution Simulator")
    print("===================================")

    simulate_agent("triage-agent")
    simulate_agent("blocked-agent")
    simulate_agent("ghost-agent")


if __name__ == "__main__":
    run_simulation()
