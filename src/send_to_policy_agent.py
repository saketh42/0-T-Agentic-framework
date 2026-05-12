"""
Step 6: Send to Gateway

Sends the decision context to the Gateway for authorization.
"""

from typing import Optional, Tuple
from schemas import (
    IdentityValidationRequest,
    AgentIdentityDecisionContext,
    IdentityAgentAuditLogEvent,
    IdentityValidationResponse
)
import uuid
from datetime import datetime


def submit_decision_context_to_gateway(
    request: IdentityValidationRequest,
    decision_context: AgentIdentityDecisionContext
) -> Tuple[Optional[IdentityAgentAuditLogEvent], Optional[IdentityValidationResponse]]:
    """
    Sends the decision context to the Policy Agent.
    
    For now, this is a stub that simulates sending to Policy Agent.
    In production, this would make an API call to the Policy Agent.
    
    Returns:
        (AuditLogEvent, None) on success
        (None, IdentityValidationResponse) on failure
    """
    print("\n" + "="*60)
    print(" STEP 6: SEND TO POLICY AGENT")
    print("="*60)
    
    print(f"\n   Sending DecisionContext to Policy Agent...")
    print(f"    Payload (Full DecisionContext):")
    print(f"      - agent_id: {decision_context.agent_id}")
    print(f"      - tenant_id: {decision_context.tenant_id}")
    print(f"      - environment: {decision_context.environment}")
    print(f"      - network_zone: {decision_context.network_zone}")
    print(f"      - origin: {decision_context.origin}")
    print(f"      - session_id: {decision_context.session_id}")
    print(f"      - status: {decision_context.status}")
    print(f"      - timestamp: {decision_context.timestamp}")
    print(f"\n       JWT Token:")
    print(f"         - token: {decision_context.token[:80]}...")
    print(f"\n       Security Posture (metadata):")
    print(f"         - agent_id: {decision_context.metadata.agent_id}")
    print(f"         - role: {decision_context.metadata.role}")
    print(f"         - risk_tier: {decision_context.metadata.risk_tier}")
    print(f"         - autonomy_level: {decision_context.metadata.autonomy_level}")
    print(f"         - allowed_tools: {decision_context.metadata.allowed_tools}")
    print(f"         - capabilities: {decision_context.metadata.capabilities}")
    print(f"         - governance_tags: {decision_context.metadata.governance_tags}")
    
    # STUB: In production, this would make an API call to Gateway
    # For now, we assume Gateway returns ALLOW for all active agents
    policy_decision = "ALLOW"
    policy_reason = "Agent is active and identity validated successfully"
    
    print(f"\n    Policy Agent Response: {policy_decision}")
    print(f"    Reason: {policy_reason}")
    
    # Create audit log
    audit_log = IdentityAgentAuditLogEvent(
        event_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        agent_id=request.agent_id,
        session_id=request.session_id,
        tenant_id=request.tenant_id,
        environment=request.environment,
        origin=request.origin,
        network_zone=request.network_zone,
        event_type="identity_validation",
        decision=policy_decision,
        reason=policy_reason
    )
    
    print(f"\n    Audit log created: event_id={audit_log.event_id}")
    
    return audit_log, None


def create_identity_allow_audit_log(request: IdentityValidationRequest, reason: str) -> IdentityAgentAuditLogEvent:
    """Create an allow audit log."""
    audit_log = IdentityAgentAuditLogEvent(
        event_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        agent_id=request.agent_id,
        session_id=request.session_id,
        tenant_id=request.tenant_id,
        environment=request.environment,
        origin=request.origin,
        network_zone=request.network_zone,
        event_type="identity_validation",
        decision="ALLOW",
        reason=reason
    )
    return audit_log