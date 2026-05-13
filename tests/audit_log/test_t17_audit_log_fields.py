"""T17: Decision context has all required fields (for success)"""

import pytest
from identity_agent import identity_agent_service


def test_audit_log_required_fields(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]
    result = identity_agent_service(payload, mock_db_active)

    # For success, check decision context has all fields
    assert result.authorization == "ALLOW"
    assert result.identity_context is not None

    required_fields = ["agent_id", "tenant_id", "environment", "network_zone",
                     "origin", "session_id", "metadata", "status", "timestamp"]

    for field in required_fields:
        assert hasattr(result.identity_context, field) and getattr(result.identity_context, field) is not None