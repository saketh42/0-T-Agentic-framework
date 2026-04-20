"""T17: Audit log has all required fields"""

import pytest
from identity_agent import identity_agent_flow


def test_audit_log_required_fields(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]
    result = identity_agent_flow(payload, mock_db_active)

    assert mock_db_active.write_audit_log.called is True

    audit_log = mock_db_active.write_audit_log.call_args[0][0]

    required_fields = ["event_id", "timestamp", "agent_id", "session_id",
                     "tenant_id", "environment", "origin", "network_zone",
                     "event_type", "decision", "reason"]

    for field in required_fields:
        assert hasattr(audit_log, field) and getattr(audit_log, field) is not None