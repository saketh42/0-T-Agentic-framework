class IdentityRequest:
    def __init__(self, agent_id, session_id, environment, tenant_id="tenant-default", origin="gateway", network_zone="internal"):
        self.agent_id = agent_id
        self.session_id = session_id
        self.environment = environment
        self.tenant_id = tenant_id
        self.origin = origin
        self.network_zone = network_zone


class DecisionContext:
    def __init__(
        self,
        agent_id,
        role,
        risk_tier,
        autonomy_level,
        allowed_tools,
        session_id,
        environment,
        tenant_id,
        origin,
        network_zone,
        capabilities
    ):
        self.agent_id = agent_id
        self.role = role
        self.risk_tier = risk_tier
        self.autonomy_level = autonomy_level
        self.allowed_tools = allowed_tools
        self.session_id = session_id
        self.environment = environment
        self.tenant_id = tenant_id
        self.origin = origin
        self.network_zone = network_zone
        self.capabilities = capabilities

    def to_dict(self):
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "risk_tier": self.risk_tier,
            "autonomy_level": self.autonomy_level,
            "allowed_tools": self.allowed_tools,
            "session_id": self.session_id,
            "environment": self.environment,
            "tenant_id": self.tenant_id,
            "origin": self.origin,
            "network_zone": self.network_zone,
            "capabilities": self.capabilities
        }


class IdentityResolutionResult:
    def __init__(self, decision, reason, agent_status=None, agent_data=None, context=None):
        self.decision = decision
        self.reason = reason
        self.agent_status = agent_status
        self.agent_data = agent_data
        self.context = context

    def to_dict(self):
        return {
            "decision": self.decision,
            "reason": self.reason,
            "agent_status": self.agent_status,
            "agent_data": self.agent_data,
            "context": self.context.to_dict() if self.context else None
        }
