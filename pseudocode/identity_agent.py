"""
Identity Agent - Agentic Security Platform

Implements the Identity & Context Service per main.md Section 6.1

Responsibilities:
- Validates agent tokens (JWT/mTLS) with claims: agent_id, role, autonomy_level, tenant_id
- Resolves agent metadata from registry (owner, capabilities, risk tier)
- Attaches context attributes: environment, network_zone, session, origin
- Builds IdentityDecisionContext passed downstream to Policy Agent

Flow (Steps 1-7):
1. Validate request
2. Look up agent in registry (separate tables per status)
3. Check active/blocked decision
4. Fetch metadata (security posture)
5. Build decision context (output contract)
6. Write audit log event
7. Return final output
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel


# ==========================================
# REQUEST SCHEMAS
# ==========================================

class IdentityRequest(BaseModel):
    agent_id: str
    tenant_id: str
    environment: str
    session_id: str
    origin: str
    network_zone: str


# ==========================================
# REGISTRY SCHEMAS - SEPARATE TABLES PER STATUS
# ==========================================

class RegistryRecord(BaseModel):
    """
    Core registry record schema (shared across all registry tables).
    Tables: registry_active, registry_suspended, registry_disabled, registry_pending
    """
    agent_id: str
    tenant_id: str
    environment: str
    ownership_team: str
    registered_at: datetime
    updated_at: datetime


# ==========================================
# METADATA SCHEMA - SECURITY POSTURE
# ==========================================

class AgentMetadata(BaseModel):
    """
    Agent metadata defining the agent's SECURITY POSTURE.
    
    Security Posture: Defines agent's trust level and capabilities:
    - role: Agent's role (e.g., "planner", "worker", "governance")
    - risk_tier: Risk exposure level (e.g., "low", "medium", "high", "critical")
    - autonomy_level: Authorized autonomy (e.g., "supervised", "autonomous")
    - allowed_tools: List of tool names agent can invoke
    - capabilities: List of agent capabilities
    - governance_tags: Tags for governance compliance
    """
    agent_id: str
    role: str
    risk_tier: str
    autonomy_level: str
    allowed_tools: List[str]
    capabilities: List[str]
    governance_tags: List[str]
    updated_at: datetime


# ==========================================
# AUDIT LOG SCHEMA
# ==========================================

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


# ==========================================
# IDENTITY DECISION CONTEXT - OUTPUT CONTRACT
# ==========================================

class IdentityDecisionContext(BaseModel):
    """
    OUTPUT CONTRACT: Passed to Policy Agent for downstream authorization.
    
    Contains agent identity + context + security posture for policy evaluation.
    """
    agent_id: str
    tenant_id: str
    environment: str
    network_zone: str
    origin: str
    session_id: str
    metadata: AgentMetadata
    status: str
    timestamp: datetime


# ==========================================
# RESPONSE SCHEMAS
# ==========================================

class InitialValidationResponse(BaseModel):
    success: bool
    agent_id: Optional[str] = None
    registry_status: Optional[str] = None
    request_context: Optional[dict] = None
    error_message: Optional[str] = None


class FinalResponse(BaseModel):
    success: bool
    decision_context: Optional[IdentityDecisionContext] = None
    audit_event_id: Optional[str] = None
    error_message: Optional[str] = None


# ==========================================
# DATABASE CLIENT INTERFACE
# ==========================================

class DatabaseClient:
    """
    Database client interface for registry and audit log operations.
    Implementation to be provided by DB Team.
    """
    
    # Registry table lookups (separate tables per status)
    def fetch_from_registry_active(self, agent_id: str) -> Optional[RegistryRecord]:
        pass
    
    def fetch_from_registry_suspended(self, agent_id: str) -> Optional[RegistryRecord]:
        pass
    
    def fetch_from_registry_disabled(self, agent_id: str) -> Optional[RegistryRecord]:
        pass
    
    def fetch_from_registry_pending(self, agent_id: str) -> Optional[RegistryRecord]:
        pass
    
    # Metadata lookup
    def fetch_agent_metadata(self, agent_id: str) -> Optional[AgentMetadata]:
        pass
    
    # Audit log write (append-only, tamper-evident)
    def write_audit_log(self, log_event: AuditLogEvent) -> bool:
        pass


# ==========================================
# IDENTITY AGENT FLOW
# ==========================================

def identity_agent_flow(
    request_payload: dict,
    db_client: Optional[DatabaseClient] = None,
) -> FinalResponse:
    """
    Main Identity Agent flow combining Steps 1-7.
    
    Returns IdentityDecisionContext (output contract) for Policy Agent.
    """
    import uuid
    
    # Step 0: Null check for db_client
    if db_client is None:
        return FinalResponse(
            success=False,
            error_message="Database client not initialized"
        )
    
    # Step 1: Validate request shape and required fields
    try:
        request = IdentityRequest(**request_payload)
    except Exception as e:
        return FinalResponse(
            success=False,
            error_message=f"Invalid request payload: {str(e)}"
        )
    
    if not request.agent_id.strip():
        return FinalResponse(
            success=False,
            error_message="Invalid request: agent_id is required"
        )
    
    if not request.tenant_id.strip():
        return FinalResponse(
            success=False,
            error_message="Invalid request: tenant_id is required"
        )
    
    if not request.environment.strip():
        return FinalResponse(
            success=False,
            error_message="Invalid request: environment is required"
        )
    
    # Step 2: Look up agent in registry (separate tables per status)
    # Try all 4 tables to find the agent
    registry_record = None
    found_status = None
    
    # Check active table
    record = db_client.fetch_from_registry_active(request.agent_id)
    if record:
        registry_record = record
        found_status = "active"
    
    # Check suspended table
    if not record:
        record = db_client.fetch_from_registry_suspended(request.agent_id)
        if record:
            registry_record = record
            found_status = "suspended"
    
    # Check disabled table
    if not record:
        record = db_client.fetch_from_registry_disabled(request.agent_id)
        if record:
            registry_record = record
            found_status = "disabled"
    
    # Check pending table
    if not record:
        record = db_client.fetch_from_registry_pending(request.agent_id)
        if record:
            registry_record = record
            found_status = "pending"
    
    # Unknown agent handling
    if not registry_record:
        return FinalResponse(
            success=False,
            error_message=(
                f"Unknown agent: {request.agent_id} "
                f"for tenant={request.tenant_id}, environment={request.environment}"
            )
        )
    
    # Step 2b: Cross-tenant leakage check
    # Verify tenant_id and environment match
    if registry_record.tenant_id != request.tenant_id:
        return FinalResponse(
            success=False,
            error_message="Cross-tenant access attempt detected"
        )
    
    if registry_record.environment != request.environment:
        return FinalResponse(
            success=False,
            error_message="Cross-environment access attempt detected"
        )
    
    # Step 3: Active/blocked/suspended/pending decision handling
    active_statuses = ["active"]
    
    if found_status not in active_statuses:
        error_msg = f"Agent {request.agent_id} is not active. Current status: {found_status}"
        
        # Step 6 (failure): Write audit log event
        audit_log = AuditLogEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            agent_id=request.agent_id,
            session_id=request.session_id,
            tenant_id=request.tenant_id,
            environment=request.environment,
            origin=request.origin,
            network_zone=request.network_zone,
            event_type="identity_validation",
            decision="DENY",
            reason=error_msg
        )
        
        try:
            db_client.write_audit_log(audit_log)
        except Exception as e:
            # Log failure but don't block the response
            pass
        
        # Step 7 (failure): Return final output
        return FinalResponse(
            success=False,
            error_message=error_msg,
            audit_event_id=audit_log.event_id
        )
    
    # Step 4: Fetch metadata (security posture)
    metadata = db_client.fetch_agent_metadata(agent_id=request.agent_id)
    if not metadata:
        error_msg = f"Missing metadata in DB for active agent {request.agent_id}"
        return FinalResponse(
            success=False,
            error_message=error_msg
        )
    
    # Step 5: Build decision context (output contract)
    decision_context = IdentityDecisionContext(
        agent_id=request.agent_id,
        tenant_id=request.tenant_id,
        environment=request.environment,
        network_zone=request.network_zone,
        origin=request.origin,
        session_id=request.session_id,
        metadata=metadata,
        status=found_status,
        timestamp=datetime.utcnow()
    )
    
    # Step 6 (success): Write audit log event
    audit_log = AuditLogEvent(
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
        reason="Agent is active and metadata successfully retrieved."
    )
    
    try:
        db_client.write_audit_log(audit_log)
    except Exception as e:
        # Log failure but don't block the response
        pass
    
    # Step 7 (success): Return final output
    return FinalResponse(
        success=True,
        decision_context=decision_context,
        audit_event_id=audit_log.event_id
    )