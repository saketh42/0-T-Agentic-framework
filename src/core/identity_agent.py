"""
Identity Agent - Core Logic

Implements the Identity & Context Service per main.md Section 6.1

Flow (Steps 1-7):
1. Validate request
2. Look up agent in registry (separate tables per status)
3. Check active/blocked decision
4. Fetch metadata (security posture)
5. Build decision context (output contract)
6. Write audit log event
7. Return final output
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from .schemas import (
    IdentityRequest,
    RegistryRecord,
    AgentMetadata,
    AuditLogEvent,
    IdentityDecisionContext,
    FinalResponse,
)
from .database import DatabaseClient


def identity_agent_flow(
    request_payload: Dict[str, Any],
    db_client: Optional[DatabaseClient] = None,
) -> FinalResponse:
    """
    Main Identity Agent flow combining Steps 1-7.
    
    Returns IdentityDecisionContext (output contract) for Policy Agent.
    """
    
    # ============================================================
    # STEP 0: Null check for db_client
    # ============================================================
    if db_client is None:
        return FinalResponse(
            success=False,
            error_message="Database client not initialized"
        )
    
    # ============================================================
    # STEP 1: Validate request payload
    # ============================================================
    # Validate required fields and structure
    try:
        request = IdentityRequest(**request_payload)
    except Exception as e:
        return FinalResponse(
            success=False,
            error_message=f"Invalid request payload: {str(e)}"
        )
    
    # Check for empty/whitespace values
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
    
    # ============================================================
    # STEP 2: Look up agent in registry
    # ============================================================
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
    
    # Cross-tenant leakage check
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
    
    # ============================================================
    # STEP 3: Check active/blocked decision
    # ============================================================
    active_statuses = ["active"]
    
    if found_status not in active_statuses:
        error_msg = f"Agent {request.agent_id} is not active. Current status: {found_status}"
        
        # Step 6 (failure): Write audit log
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
        except Exception:
            pass
        
        # Step 7 (failure): Return error
        return FinalResponse(
            success=False,
            error_message=error_msg,
            audit_event_id=audit_log.event_id
        )
    
    # ============================================================
    # STEP 4: Fetch metadata
    # ============================================================
    metadata = db_client.fetch_agent_metadata(agent_id=request.agent_id)
    if not metadata:
        error_msg = f"Missing metadata in DB for active agent {request.agent_id}"
        return FinalResponse(
            success=False,
            error_message=error_msg
        )
    
    # ============================================================
    # STEP 5: Build decision context
    # ============================================================
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
    
    # ============================================================
    # STEP 6: Write audit log (success)
    # ============================================================
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
    except Exception:
        pass
    
    # ============================================================
    # STEP 7: Return final output
    # ============================================================
    return FinalResponse(
        success=True,
        decision_context=decision_context,
        audit_event_id=audit_log.event_id
    )