class IdentityRequest:
    def __init__(self, agent_id, session_id, environment):
        self.agent_id = agent_id
        self.session_id = session_id
        self.environment = environment


class DecisionContext:
    def __init__(self, agent_id, role, risk_tier, autonomy_level, allowed_tools, session_id, environment):
        self.agent_id = agent_id
        self.role = role
        self.risk_tier = risk_tier
        self.autonomy_level = autonomy_level
        self.allowed_tools = allowed_tools
        self.session_id = session_id
        self.environment = environment

    def to_dict(self):
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "risk_tier": self.risk_tier,
            "autonomy_level": self.autonomy_level,
            "allowed_tools": self.allowed_tools,
            "session_id": self.session_id,
            "environment": self.environment
        }