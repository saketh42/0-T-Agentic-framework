"""T12: Disabled agent denied"""

import pytest
from identity_agent import identity_agent_flow


def test_disabled_agent(test_inputs, mock_db_disabled):
    payload = test_inputs["disabled_agent"]
    result = identity_agent_flow(payload, mock_db_disabled)

    assert result.success is False
    assert "disabled" in result.error_message.lower()