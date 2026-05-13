"""T21: Security posture - governance_tags passed through"""

import pytest
from identity_agent import identity_agent_service


def test_security_posture_governance_tags(test_inputs, mock_db_high_risk):
    payload = test_inputs["high_risk_agent"]
    result = identity_agent_service(payload, mock_db_high_risk)

    assert result.authorization == "ALLOW"
    assert result.identity_context is not None

    expected_tags = ["pci", "hipaa", "fedramp"]
    actual_tags = result.identity_context.metadata.governance_tags

    assert set(expected_tags) == set(actual_tags)