"""T01: Valid request returns success"""

import pytest
from identity_agent import identity_agent_flow


def test_valid_request_returns_success(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]
    result = identity_agent_flow(payload, mock_db_active)

    assert result.success is True
    assert result.decision_context is not None
    assert result.decision_context.agent_id == "agent-001"
    assert result.decision_context.status == "active"