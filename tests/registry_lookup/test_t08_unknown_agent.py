"""T08: Unknown agent"""

import pytest
from core.identity_agent import identity_agent_flow


def test_unknown_agent(test_inputs, mock_db_unknown):
    payload = test_inputs["unknown_agent"]
    result = identity_agent_flow(payload, mock_db_unknown)

    assert result.success is False
    assert "unknown agent" in result.error_message.lower()