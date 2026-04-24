"""
Identity Agent - Driver (PostgreSQL)

This is the driver that uses PostgreSQL as the database.
Used for integration testing with real database.
"""

import sys
sys.path.insert(0, '.')

from postgres_client import PostgresDatabaseClient
from identity_agent import identity_agent_flow


def run_test(db, agent_id: str, description: str):
    """Run a test case."""
    print("\n" + "="*60)
    print(f"🧪 TEST: {description}")
    print("="*60)
    
    result = identity_agent_flow({
        'agent_id': agent_id,
        'tenant_id': 'tenant-acme',
        'environment': 'prod',
        'session_id': 'sess-123',
        'origin': '192.168.1.100',
        'network_zone': 'dmz'
    }, db)
    
    print("\n" + "="*60)
    print("📤 FINAL OUTPUT")
    print("="*60)
    print(f"\n   Success: {result.success}")
    
    if result.success:
        print("\n   ✅ ACCESS GRANTED - Sent to Policy Agent")
        print(f"\n   📥 Request Context (sent to Policy Agent):")
        print(f"      - agent_id:     {result.decision_context.agent_id}")
        print(f"      - tenant_id:    {result.decision_context.tenant_id}")
        print(f"      - environment:  {result.decision_context.environment}")
        print(f"      - session_id:   {result.decision_context.session_id}")
        print(f"      - origin:       {result.decision_context.origin}")
        print(f"      - network_zone: {result.decision_context.network_zone}")
        print(f"      - status:       {result.decision_context.status}")
        print(f"      - timestamp:    {result.decision_context.timestamp}")
        print(f"\n   📋 Security Posture (metadata):")
        print(f"      - role:           {result.decision_context.metadata.role}")
        print(f"      - risk_tier:     {result.decision_context.metadata.risk_tier}")
        print(f"      - autonomy_level: {result.decision_context.metadata.autonomy_level}")
        print(f"      - allowed_tools:  {', '.join(result.decision_context.metadata.allowed_tools)}")
        print(f"      - capabilities:   {', '.join(result.decision_context.metadata.capabilities)}")
        print(f"      - governance_tags: {', '.join(result.decision_context.metadata.governance_tags)}")
        print(f"\n   📝 Audit Event ID: {result.audit_event_id}")
    else:
        print("\n   ❌ ACCESS DENIED")
        print(f"   Error: {result.error_message}")
    
    print(f"\n   Audit Event ID: {result.audit_event_id}")
    
    return result


def main():
    print("\n" + "="*60)
    print("🎯 IDENTITY AGENT - PostgreSQL Driver")
    print("="*60)
    
    # Connect to PostgreSQL
    print("\n🔌 Connecting to PostgreSQL...")
    db = PostgresDatabaseClient()
    print("   ✅ Connected\n")
    
    # Test cases
    test_cases = [
        ("agent-001", "Active Agent - Should Pass"),
        ("agent-002", "Suspended Agent - Should Deny"),
        ("agent-highrisk", "High Risk Active Agent - Should Pass"),
        ("unknown-agent", "Unknown Agent - Should Deny"),
    ]
    
    for agent_id, description in test_cases:
        run_test(db, agent_id, description)
    
    # Show audit logs
    print("\n" + "="*60)
    print("📋 AUDIT LOGS IN DATABASE")
    print("="*60)
    with db.connection.cursor() as cursor:
        cursor.execute('SELECT log_id, agent_id, decision, reason FROM audit_logs ORDER BY timestamp')
        print(f"\n{'event_id':<38} {'agent_id':<15} {'decision':<8} {'reason'}")
        print("-" * 100)
        for row in cursor.fetchall():
            print(f"{row[0]:<38} {row[1]:<15} {row[2]:<8} {row[3][:50]}...")
    
    db.close()
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)


if __name__ == "__main__":
    main()