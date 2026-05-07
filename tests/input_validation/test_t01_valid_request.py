"""T01: Valid request returns success"""

import pytest
from identity_agent import identity_agent_service


def test_valid_request_returns_success(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]
    result = identity_agent_service(payload, mock_db_active)

    assert result.is_authorized is True
    assert result.identity_context is not None
    assert result.identity_context.agent_id == "agent-001"
    assert result.identity_context.status == "active"