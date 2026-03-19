# context_builder.py

from models import DecisionContext


def build_context(agent_id, agent_data, session_id, environment):

    print("[ContextBuilder] Constructing Decision Context")

    print("[ContextBuilder] Agent role:", agent_data["role"])
    print("[ContextBuilder] Risk tier:", agent_data["risk_tier"])
    print("[ContextBuilder] Autonomy level:", agent_data["autonomy_level"])
    print("[ContextBuilder] Tenant ID:", agent_data["tenant_id"])
    print("[ContextBuilder] Origin:", agent_data["origin"])
    print("[ContextBuilder] Network zone:", agent_data["network_zone"])

    context = DecisionContext(
        agent_id=agent_id,
        role=agent_data["role"],
        risk_tier=agent_data["risk_tier"],
        autonomy_level=agent_data["autonomy_level"],
        allowed_tools=agent_data["allowed_tools"],
        session_id=session_id,
        environment=environment,
        tenant_id=agent_data["tenant_id"],
        origin=agent_data["origin"],
        network_zone=agent_data["network_zone"],
        capabilities=agent_data["capabilities"]
    )

    print("[ContextBuilder] Decision Context ready")

    return context
