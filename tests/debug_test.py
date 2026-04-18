import sys
sys.path.insert(0, '.')
from identity_agent import *

payload = {'agent_id': 'agent-001', 'tenant_id': 'tenant-acme', 'environment': 'prod', 'session_id': 'sess-12345'}

from unittest.mock import Mock
mock = Mock()

# Set up mock to simulate unknown agent - will fail before audit log
result = identity_agent_flow(payload, mock)
print('Result:', result)
print('write_audit_log called:', mock.write_audit_log.called)