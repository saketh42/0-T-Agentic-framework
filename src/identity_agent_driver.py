"""
Identity Agent - Driver (PostgreSQL)
 
This is the driver that uses PostgreSQL as the database.
Used for integration testing with real database.
"""

import sys
import os
sys.path.insert(0, '.')

from postgres_client import PostgresIdentityAgentDatabaseClient
from identity_agent import identity_agent_service

# Optional STM client (non-breaking)
try:
    from stm_redis_client import RedisAgentShortTermMemoryClient
    STM_AVAILABLE = True
except ImportError:
    STM_AVAILABLE = False


def run_test(db, agent_id: str, description: str, stm_client=None):
    """Run a test case."""
    print("\n" + "="*60)
    print(f" TEST: {description}")
    print("="*60)
    
    result = identity_agent_service({
        'agent_id': agent_id,
        'tenant_id': 'tenant-acme',
        'environment': 'prod',
        'session_id': 'sess-123',
        'origin': '192.168.1.100',
        'network_zone': 'dmz'
    }, db, stm_client)
    
    print("\n" + "="*60)
    print(" FINAL OUTPUT")
    print("="*60)
    print(f"\n   Success: {result.authorization}")
    
    if result.authorization == "ALLOW":
        print("\n    ACCESS GRANTED - Sent to Policy Agent")
        print(f"\n    Request Context (sent to Policy Agent):")
        print(f"      - agent_id:     {result.identity_context.agent_id}")
        print(f"      - tenant_id:    {result.identity_context.tenant_id}")
        print(f"      - environment:  {result.identity_context.environment}")
        print(f"      - session_id:   {result.identity_context.session_id}")
        print(f"      - origin:       {result.identity_context.origin}")
        print(f"      - network_zone: {result.identity_context.network_zone}")
        print(f"      - status:       {result.identity_context.status}")
        print(f"      - timestamp:    {result.identity_context.timestamp}")
        print(f"\n    Security Posture (metadata):")
        print(f"      - role:           {result.identity_context.metadata.role}")
        print(f"      - risk_tier:     {result.identity_context.metadata.risk_tier}")
        print(f"      - autonomy_level: {result.identity_context.metadata.autonomy_level}")
        print(f"      - allowed_tools:  {', '.join(result.identity_context.metadata.allowed_tools)}")
        print(f"      - capabilities:   {', '.join(result.identity_context.metadata.capabilities)}")
        print(f"      - governance_tags: {', '.join(result.identity_context.metadata.governance_tags)}")
    elif result.authorization == "BLOCK":
        print("\n    ACCESS BLOCKED - Unknown Agent")
        print(f"   Error: {result.failure_reason}")
    else:
        print("\n    ACCESS DENIED")
        print(f"   Error: {result.failure_reason}")
    
    return result


def main():
    print("\n" + "="*60)
    print(" IDENTITY AGENT - PostgreSQL Driver")
    print("="*60)
    
    # Connect to PostgreSQL
    print("\n Connecting to PostgreSQL...")
    db = PostgresIdentityAgentDatabaseClient()
    print("    Connected\n")
    
    # Optional STM client (non-breaking)
    stm = None
    if STM_AVAILABLE and os.getenv("USE_STM"):
        try:
            stm = RedisAgentShortTermMemoryClient()
            print("    STM (Redis) Connected\n")
        except Exception as e:
            print(f"    STM init failed (non-critical): {e}\n")
    
    # Test cases
    test_cases = [
        ("agent-001", "Active Agent - Should Pass"),
        ("agent-002", "Suspended Agent - Should Deny"),
        ("agent-highrisk", "High Risk Active Agent - Should Pass"),
        ("unknown-agent", "Unknown Agent - Should Deny"),
    ]
    
    for agent_id, description in test_cases:
        run_test(db, agent_id, description, stm)
    
    db.close()
    print("\n" + "="*60)
    print(" ALL TESTS COMPLETED")
    print("="*60)


if __name__ == "__main__":
    main()