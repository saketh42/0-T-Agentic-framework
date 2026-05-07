"""
Step 5: Build Decision Context

Builds the decision context from the agent information.
"""

from typing import Optional
from datetime import datetime
from schemas import (
    IdentityValidationRequest,
    AgentRegistryRecord,
    AgentSecurityMetadata,
    AgentIdentityDecisionContext
)


def build_identity_decision_context(
    request: IdentityValidationRequest,
    metadata: AgentSecurityMetadata,
    status: str
) -> AgentIdentityDecisionContext:
    """
    Builds the decision context from agent information.
    
    Returns:
        IdentityDecisionContext
    """
    print("\n" + "="*60)
    print(" STEP 5: BUILD DECISION CONTEXT")
    print("="*60)
    
    decision_context = AgentIdentityDecisionContext(
        agent_id=request.agent_id,
        tenant_id=request.tenant_id,
        environment=request.environment,
        network_zone=request.network_zone,
        origin=request.origin,
        session_id=request.session_id,
        metadata=metadata,
        status=status,
        timestamp=datetime.utcnow()
    )
    
    print("    Decision context built")
    print(f"\n    Decision Context Output:")
    print(f"      - agent_id: {decision_context.agent_id}")
    print(f"      - tenant_id: {decision_context.tenant_id}")
    print(f"      - environment: {decision_context.environment}")
    print(f"      - status: {decision_context.status}")
    print(f"      - network_zone: {decision_context.network_zone}")
    print(f"      - origin: {decision_context.origin}")
    print(f"      - session_id: {decision_context.session_id}")
    print(f"      - timestamp: {decision_context.timestamp}")
    print(f"\n       Security Posture:")
    print(f"         - role: {decision_context.metadata.role}")
    print(f"         - risk_tier: {decision_context.metadata.risk_tier}")
    print(f"         - autonomy_level: {decision_context.metadata.autonomy_level}")
    print(f"         - allowed_tools: {decision_context.metadata.allowed_tools}")
    print(f"         - capabilities: {decision_context.metadata.capabilities}")
    print(f"         - governance_tags: {decision_context.metadata.governance_tags}")
    
    return decision_context