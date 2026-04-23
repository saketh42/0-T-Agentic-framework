"""T24: Decision context has all required fields"""

import pytest
from core.identity_agent import identity_agent_flow


def test_decision_context_all_fields(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]
    result = identity_agent_flow(payload, mock_db_active)

    assert result.decision_context is not None

    required_fields = ["agent_id", "tenant_id", "environment", "network_zone",
                  "origin", "session_id", "metadata", "status", "timestamp"]

    for field in required_fields:
        assert hasattr(result.decision_context, field)
        assert getattr(result.decision_context, field) is not None