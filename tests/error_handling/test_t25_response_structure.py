"""T25: FinalResponse has correct structure"""

import pytest
from identity_agent import identity_agent_flow


def test_response_structure_success(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]
    result = identity_agent_flow(payload, mock_db_active)

    assert result.decision_context is not None
    assert result.audit_event_id is not None
    assert result.error_message is None


def test_response_structure_failure(test_inputs, mock_db_suspended):
    payload = test_inputs["suspended_agent"]
    result = identity_agent_flow(payload, mock_db_suspended)

    assert result.decision_context is None
    assert result.error_message is not None
    assert result.audit_event_id is not None