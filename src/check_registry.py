"""
Step 3: Check Registry

Checks the agent registry for the agent and validates tenant/environment.
"""

from typing import Optional, Tuple
from database import IdentityAgentDatabaseClient
from schemas import IdentityValidationRequest, AgentRegistryRecord, IdentityValidationResponse


def lookup_agent_in_identity_registry(
    request: IdentityValidationRequest,
    db_client: IdentityAgentDatabaseClient
) -> Tuple[Optional[AgentRegistryRecord], Optional[str], Optional[IdentityValidationResponse]]:
    """
    Checks the agent registry for the agent.
    
    Returns:
        (AgentRegistryRecord, status, None) on success
        (None, None, IdentityValidationResponse) on failure
    """
    print("\n" + "="*60)
    print(" STEP 3: CHECK REGISTRY")
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
        print(f"    Found in active table")
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
            print(f"    Found in suspended table")
    
    # Check disabled table
    if not record:
        print("   Checking 'disabled' table...")
        record = db_client.fetch_from_registry_disabled(request.agent_id)
        if record:
            registry_record = record
            found_status = "disabled"
            print(f"    Found in disabled table")
    
    # Check pending table
    if not record:
        print("   Checking 'pending' table...")
        record = db_client.fetch_from_registry_pending(request.agent_id)
        if record:
            registry_record = record
            found_status = "pending"
            print(f"    Found in pending table")
    
    # Agent not found
    if not registry_record:
        print(f"    Agent not found: {request.agent_id}")
        error_msg = f"Unknown agent: {request.agent_id} for tenant={request.tenant_id}, environment={request.environment}"
        error = IdentityValidationResponse(authorization="BLOCK", failure_reason=error_msg)
        return None, None, error
    
    print(f"\n   Status: {found_status}")
    
    # Cross-tenant check
    print("\n   Checking cross-tenant...")
    if registry_record.tenant_id != request.tenant_id:
        print(f"    Cross-tenant detected!")
        print(f"      - Request tenant: {request.tenant_id}")
        print(f"      - Registry tenant: {registry_record.tenant_id}")
        error_msg = "Cross-tenant access attempt detected"
        error = IdentityValidationResponse(authorization="DENY", failure_reason=error_msg)
        return None, None, error
    print("    Tenant matches")
    
    # Check if agent is active
    if found_status != "active":
        print(f"\n    Agent is {found_status}, not active")
        error_msg = f"Agent {request.agent_id} is not active. Current status: {found_status}"
        error = IdentityValidationResponse(authorization="DENY", failure_reason=error_msg)
        return None, None, error
    
    print("\n    Agent is active and authorized")
    return registry_record, found_status, None
