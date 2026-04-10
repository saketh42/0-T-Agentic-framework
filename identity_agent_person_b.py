from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

# ==========================================
# SCHEMAS FOR DB TEAM (Person B Ownership)
# ==========================================

class AgentMetadata(BaseModel):
    agent_id: str
    role: str
    risk_tier: str
    autonomy_level: str
    allowed_tools: list[str]
    capabilities: list[str]
    governance_tags: list[str]
    updated_at: datetime

class AuditLogEvent(BaseModel):
    event_id: str
    timestamp: datetime
    agent_id: str
    session_id: str
    tenant_id: str
    environment: str
    origin: str
    network_zone: str
    event_type: str
    decision: str
    reason: str
    hash: Optional[str] = None
    tamper_proof_ref: Optional[str] = None

class DecisionContext(BaseModel):
    agent_id: str
    tenant_id: str
    environment: str
    network_zone: str
    origin: str
    session_id: str
    metadata: AgentMetadata
    status: str
    timestamp: datetime

class FinalResponse(BaseModel):
    success: bool
    decision_context: Optional[DecisionContext] = None
    audit_event_id: Optional[str] = None
    error_message: Optional[str] = None


# ==========================================
# MOCK DATABASE INTERFACES
# ==========================================

class DatabaseClientPlaceholder:
    def fetch_agent_metadata(self, agent_id: str) -> Optional[AgentMetadata]:
        # Implementation to be provided by DB Team
        pass
    
    def write_audit_log(self, log_event: AuditLogEvent) -> bool:
        # Implementation to be provided by DB Team (Append-only tamper-evident log)
        pass


# ==========================================
# PERSON B: ENRICHMENT AND OUTPUT FLOW
# ==========================================

def person_b_enrichment_flow(
    agent_id: str, 
    registry_status: str, 
    request_context: Dict[str, Any],
    db_client: DatabaseClientPlaceholder
) -> FinalResponse:
    """
    Executes Steps 3-7 for the Identity Agent (Person B Ownership)
    
    Expected Inputs from Person A (Steps 1 & 2):
    - agent_id (validated)
    - registry_status (from Registry DB: "active", "blocked", etc.)
    - request_context (dict with origin, network_zone, session_id, tenant_id, environment)
    """
    import uuid

    # Step 3: Active/blocked decision handling
    if registry_status != "active":
        error_msg = f"Agent {agent_id} is not active. Current status: {registry_status}"
        
        # Step 6 for Failure: Write audit log event
        audit_log = AuditLogEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            agent_id=agent_id,
            session_id=request_context.get("session_id", "unknown"),
            tenant_id=request_context.get("tenant_id", "unknown"),
            environment=request_context.get("environment", "unknown"),
            origin=request_context.get("origin", "unknown"),
            network_zone=request_context.get("network_zone", "unknown"),
            event_type="identity_validation",
            decision="DENY",
            reason=error_msg
        )
        db_client.write_audit_log(audit_log)
        
        # Step 7 for Failure: Return final output
        return FinalResponse(
            success=False,
            error_message=error_msg,
            audit_event_id=audit_log.event_id
        )

    # Step 4: Fetch metadata
    metadata = db_client.fetch_agent_metadata(agent_id=agent_id)
    if not metadata:
        error_msg = f"Missing metadata in DB for active agent {agent_id}"
        return FinalResponse(
            success=False,
            error_message=error_msg
        )

    # Step 5: Build decision context
    decision_context = DecisionContext(
        agent_id=agent_id,
        tenant_id=request_context.get("tenant_id", "unknown"),
        environment=request_context.get("environment", "unknown"),
        network_zone=request_context.get("network_zone", "unknown"),
        origin=request_context.get("origin", "unknown"),
        session_id=request_context.get("session_id", "unknown"),
        metadata=metadata,
        status=registry_status,
        timestamp=datetime.utcnow()
    )

    # Step 6 for Success: Write audit log event
    audit_log = AuditLogEvent(
        event_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        agent_id=agent_id,
        session_id=request_context.get("session_id", "unknown"),
        tenant_id=request_context.get("tenant_id", "unknown"),
        environment=request_context.get("environment", "unknown"),
        origin=request_context.get("origin", "unknown"),
        network_zone=request_context.get("network_zone", "unknown"),
        event_type="identity_validation",
        decision="ALLOW",
        reason="Agent is active and metadata successfully retrieved."
    )
    db_client.write_audit_log(audit_log)

    # Step 7 for Success: Return final output
    return FinalResponse(
        success=True,
        decision_context=decision_context,
        audit_event_id=audit_log.event_id
    )
