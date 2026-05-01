"""
Identity Agent - Interactive Menu

Usage: python3 run.py
"""

import sys
sys.path.insert(0, 'core')

from postgres_client import PostgresDatabaseClient
from identity_agent import identity_agent_service


def main():
    print("\n" + "="*60)
    print(" IDENTITY AGENT - Interactive Testing")
    print("="*60 + "\n")
    
    db = PostgresDatabaseClient()
    
    agents = [
        ("1", "agent-001", "Active Agent"),
        ("2", "agent-002", "Suspended Agent"),
        ("3", "agent-highrisk", "High Risk Active Agent"),
        ("4", "unknown-agent", "Unknown Agent"),
    ]
    
    print("\nAvailable Agents:")
    print("-" * 40)
    for num, agent_id, desc in agents:
        print(f"  {num}. {desc} ({agent_id})")
    print("-" * 40)
    
    choice = input("\nEnter agent number (1-4): ").strip()
    
    agent_id = None
    for num, aid, desc in agents:
        if choice == num:
            agent_id = aid
            break
    
    if not agent_id:
        print("Invalid choice!")
        return
    
    print(f"\n{'='*60}")
    print(f" Testing Agent: {agent_id}")
    print('='*60)
    
    result = identity_agent_service({
        'agent_id': agent_id,
        'tenant_id': 'tenant-acme',
        'environment': 'prod',
        'session_id': 'sess-123',
        'origin': '192.168.1.100',
        'network_zone': 'dmz'
    }, db)
    
    print("\n" + "="*60)
    print(" FINAL OUTPUT")
    print("="*60)
    print(f"\nSuccess: {result.is_authorized}")
    
    if result.is_authorized:
        print("\n ACCESS GRANTED")
        print(f"\n  Agent ID:       {result.identity_context.agent_id}")
        print(f"  Tenant ID:      {result.identity_context.tenant_id}")
        print(f"  Environment:    {result.identity_context.environment}")
        print(f"  Status:         {result.identity_context.status}")
        print(f"\n   Security Posture:")
        print(f"     Role:          {result.identity_context.metadata.role}")
        print(f"     Risk Tier:     {result.identity_context.metadata.risk_tier}")
        print(f"     Autonomy:      {result.identity_context.metadata.autonomy_level}")
        print(f"     Allowed Tools: {', '.join(result.identity_context.metadata.allowed_tools)}")
        print(f"     Governance:    {', '.join(result.identity_context.metadata.governance_tags)}")
    else:
        print("\n ACCESS DENIED")
        print(f"\n  Error: {result.failure_reason}")
    
    print(f"\n  Audit Event ID: {result.audit_log_id}")
    print("\n" + "="*60)
    
    db.close()


if __name__ == "__main__":
    main()