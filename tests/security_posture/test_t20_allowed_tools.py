"""T20: Security posture - allowed_tools passed through"""

import pytest
from identity_agent import identity_agent_service


def test_security_posture_allowed_tools(test_inputs, mock_db_high_risk):
    payload = test_inputs["high_risk_agent"]
    result = identity_agent_service(payload, mock_db_high_risk)

    assert result.authorization == "ALLOW"
    assert result.identity_context is not None

    expected_tools = ["containment", "quarantine", "block_ip"]
    actual_tools = result.identity_context.metadata.allowed_tools

    assert set(expected_tools) == set(actual_tools)