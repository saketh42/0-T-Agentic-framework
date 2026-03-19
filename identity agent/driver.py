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
        environment="production"
    )

    print("\n[Driver] Generated Request")
    print(vars(request))

    try:

        context = resolve_identity(request)

        print("\n[Driver] Identity Resolution SUCCESS")

        print("[Driver] Decision Context Output:")
        print(context.to_dict())

    except Exception as e:

        reason = str(e)

        print("\n[Driver] Identity Resolution FAILED")

        if reason == "UNKNOWN_AGENT":
            print("[Driver] Reason: Agent not registered")

        elif reason == "AGENT_SUSPENDED":
            print("[Driver] Reason: Agent suspended / blocked")

        else:
            print("[Driver] Error:", reason)


def run_simulation():

    print("\n===================================")
    print("Agent Identity Resolution Simulator")
    print("===================================")

    simulate_agent("triage-agent")
    simulate_agent("blocked-agent")
    simulate_agent("ghost-agent")


if __name__ == "__main__":
    run_simulation()