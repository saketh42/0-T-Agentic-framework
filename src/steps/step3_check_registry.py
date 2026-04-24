"""
Step 3: Check Registry

Checks the agent registry for the agent and validates tenant/environment.
"""

from typing import Optional, Tuple
from database import DatabaseClient
from schemas import IdentityRequest, RegistryRecord, FinalResponse, AuditLogEvent
import uuid
from datetime import datetime


def check_registry(
    request: IdentityRequest,
    db_client: DatabaseClient
) -> Tuple[Optional[RegistryRecord], Optional[str], Optional[FinalResponse], Optional[AuditLogEvent]]:
    """
    Checks the agent registry for the agent.
    
    Returns:
        (RegistryRecord, status, None, audit_log) on success
        (None, None, FinalResponse, audit_log) on failure
    """
    print("\n" + "="*60)
    print("🔍 STEP 3: CHECK REGISTRY")
    print("="*60)
    print(f"\n   Looking for agent: {request.agent_id}")
    
    registry_record = None
    found_status = None
    
    # Check active table
    print("   Checking 'active' table...")
    record = db_client.fetch_from_registry_active(request.agent_id)
    if record:
        registry_record = record
        found_status = "active"
        print(f"   ✅ Found in active table")
        print(f"      - agent_id: {registry_record.agent_id}")
        print(f"      - tenant_id: {registry_record.tenant_id}")
        print(f"      - environment: {registry_record.environment}")
        print(f"      - ownership_team: {registry_record.ownership_team}")
    
    # Check suspended table
    if not record:
        print("   Checking 'suspended' table...")
        record = db_client.fetch_from_registry_suspended(request.agent_id)
        if record:
            registry_record = record
            found_status = "suspended"
            print(f"   ✅ Found in suspended table")
    
    # Check disabled table
    if not record:
        print("   Checking 'disabled' table...")
        record = db_client.fetch_from_registry_disabled(request.agent_id)
        if record:
            registry_record = record
            found_status = "disabled"
            print(f"   ✅ Found in disabled table")
    
    # Check pending table
    if not record:
        print("   Checking 'pending' table...")
        record = db_client.fetch_from_registry_pending(request.agent_id)
        if record:
            registry_record = record
            found_status = "pending"
            print(f"   ✅ Found in pending table")
    
    # Agent not found
    if not registry_record:
        print(f"   ❌ Agent not found: {request.agent_id}")
        error_msg = f"Unknown agent: {request.agent_id} for tenant={request.tenant_id}, environment={request.environment}"
        audit_log = create_deny_audit_log(request, error_msg)
        error = FinalResponse(success=False, error_message=error_msg)
        return None, None, error, audit_log
    
    print(f"\n   Status: {found_status}")
    
    # Cross-tenant check
    print("\n   Checking cross-tenant...")
    if registry_record.tenant_id != request.tenant_id:
        print(f"   ❌ Cross-tenant detected!")
        print(f"      - Request tenant: {request.tenant_id}")
        print(f"      - Registry tenant: {registry_record.tenant_id}")
        error_msg = "Cross-tenant access attempt detected"
        audit_log = create_deny_audit_log(request, error_msg)
        error = FinalResponse(success=False, error_message=error_msg)
        return None, None, error, audit_log
    print("   ✅ Tenant matches")
    
    # Cross-environment check
    print("\n   Checking cross-environment...")
    if registry_record.environment != request.environment:
        print(f"   ❌ Cross-environment detected!")
        error_msg = "Cross-environment access attempt detected"
        audit_log = create_deny_audit_log(request, error_msg)
        error = FinalResponse(success=False, error_message=error_msg)
        return None, None, error, audit_log
    print("   ✅ Environment matches")
    
    # Check if agent is active
    if found_status != "active":
        print(f"\n   ❌ Agent is {found_status}, not active")
        error_msg = f"Agent {request.agent_id} is not active. Current status: {found_status}"
        audit_log = create_deny_audit_log(request, error_msg)
        error = FinalResponse(success=False, error_message=error_msg, audit_event_id=audit_log.event_id)
        return None, None, error, audit_log
    
    print("\n   ✅ Agent is active and authorized")
    audit_log = None
    return registry_record, found_status, None, audit_log


def create_deny_audit_log(request: IdentityRequest, reason: str) -> AuditLogEvent:
    """Create a deny audit log."""
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
        reason=reason
    )
    print(f"   📝 Audit log created: decision=DENY, reason={reason}")
    return audit_log