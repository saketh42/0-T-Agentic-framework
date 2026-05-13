"""T13: Pending agent denied"""

import pytest
from identity_agent import identity_agent_service


def test_pending_agent(test_inputs, mock_db_pending):
    payload = test_inputs["pending_agent"]
    result = identity_agent_service(payload, mock_db_pending)

    assert result.authorization == "DENY"
    assert "pending" in result.failure_reason.lower()