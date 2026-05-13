"""
Step 4: Fetch Metadata

Fetches the agent's metadata from the database.
"""

from typing import Optional, Tuple
from database import IdentityAgentDatabaseClient
from schemas import IdentityValidationRequest, AgentRegistryRecord, AgentSecurityMetadata, IdentityValidationResponse


def fetch_agent_security_metadata(
    agent_id: str,
    db_client: IdentityAgentDatabaseClient
) -> Tuple[Optional[AgentSecurityMetadata], Optional[IdentityValidationResponse]]:
    """
    Fetches the agent's metadata from the database.
    
    Returns:
        (AgentSecurityMetadata, None) on success
        (None, IdentityValidationResponse) on failure
    """
    print("\n" + "="*60)
    print(" STEP 4: FETCH METADATA")
    print("="*60)
    print(f"\n   Fetching metadata for: {agent_id}")
    
    metadata = db_client.fetch_agent_security_metadata(agent_id)
    
    if not metadata:
        error = IdentityValidationResponse(
            authorization="DENY",
            failure_reason=f"Missing metadata in DB for agent {agent_id}"
        )
        print(f"    Metadata not found")
        return None, error
    
    print("    Metadata fetched successfully")
    print(f"\n    Security Posture:")
    print(f"      - role: {metadata.role}")
    print(f"      - risk_tier: {metadata.risk_tier}")
    print(f"      - autonomy_level: {metadata.autonomy_level}")
    print(f"      - allowed_tools: {metadata.allowed_tools}")
    print(f"      - capabilities: {metadata.capabilities}")
    print(f"      - governance_tags: {metadata.governance_tags}")
    
    return metadata, None