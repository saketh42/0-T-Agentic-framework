"""T06: Whitespace-only agent_id"""

import pytest
from identity_agent import identity_agent_flow


def test_whitespace_agent_id(test_inputs, mock_db_active):
    payload = test_inputs["whitespace_agent_id"]
    result = identity_agent_flow(payload, mock_db_active)

    assert result.success is False
    assert "agent_id" in result.error_message.lower()