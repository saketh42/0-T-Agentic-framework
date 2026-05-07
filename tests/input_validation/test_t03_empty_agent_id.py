"""T03: Empty agent_id"""

import pytest
from identity_agent import identity_agent_service


def test_empty_agent_id(test_inputs, mock_db_active):
    payload = test_inputs["empty_agent_id"]
    result = identity_agent_service(payload, mock_db_active)

    assert result.is_authorized is False
    assert "agent_id" in result.failure_reason.lower()