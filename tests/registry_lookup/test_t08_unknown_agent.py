"""T08: Unknown agent"""

import pytest
from identity_agent import identity_agent_service


def test_unknown_agent(test_inputs, mock_db_unknown):
    payload = test_inputs["unknown_agent"]
    result = identity_agent_service(payload, mock_db_unknown)

    assert result.is_authorized is False
    assert "unknown agent" in result.failure_reason.lower()