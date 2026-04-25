"""T17: Decision context has all required fields (for success)"""

import pytest
from identity_agent import identity_agent_flow


def test_audit_log_required_fields(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]
    result = identity_agent_flow(payload, mock_db_active)

    # For success, check decision context has all fields
    assert result.success is True
    assert result.decision_context is not None

    required_fields = ["agent_id", "tenant_id", "environment", "network_zone",
                     "origin", "session_id", "metadata", "status", "timestamp"]

    for field in required_fields:
        assert hasattr(result.decision_context, field) and getattr(result.decision_context, field) is not None