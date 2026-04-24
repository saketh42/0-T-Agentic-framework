"""T21: Security posture - governance_tags passed through"""

import pytest
from identity_agent import identity_agent_flow


def test_security_posture_governance_tags(test_inputs, mock_db_high_risk):
    payload = test_inputs["high_risk_agent"]
    result = identity_agent_flow(payload, mock_db_high_risk)

    assert result.success is True
    assert result.decision_context is not None

    expected_tags = ["pci", "hipaa", "fedramp"]
    actual_tags = result.decision_context.metadata.governance_tags

    assert set(expected_tags) == set(actual_tags)