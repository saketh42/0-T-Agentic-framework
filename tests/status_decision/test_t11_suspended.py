"""T11: Suspended agent denied"""

import pytest
from identity_agent import identity_agent_service


def test_suspended_agent(test_inputs, mock_db_suspended):
    payload = test_inputs["suspended_agent"]
    result = identity_agent_service(payload, mock_db_suspended)

    assert result.authorization == "DENY"
    assert "suspended" in result.failure_reason.lower()