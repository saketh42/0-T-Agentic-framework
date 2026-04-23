"""T20: Security posture - allowed_tools passed through"""

import pytest
from core.identity_agent import identity_agent_flow


def test_security_posture_allowed_tools(test_inputs, mock_db_high_risk):
    payload = test_inputs["high_risk_agent"]
    result = identity_agent_flow(payload, mock_db_high_risk)

    assert result.success is True
    assert result.decision_context is not None

    expected_tools = ["containment", "quarantine", "block_ip"]
    actual_tools = result.decision_context.metadata.allowed_tools

    assert set(expected_tools) == set(actual_tools)