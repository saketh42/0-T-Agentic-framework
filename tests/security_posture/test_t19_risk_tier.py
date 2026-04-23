"""T19: Security posture - risk_tier passed through"""

import pytest
from core.identity_agent import identity_agent_flow


def test_security_posture_risk_tier(test_inputs, mock_db_high_risk):
    payload = test_inputs["high_risk_agent"]
    result = identity_agent_flow(payload, mock_db_high_risk)

    assert result.success is True
    assert result.decision_context is not None

    assert result.decision_context.metadata.risk_tier == "critical"
    assert result.decision_context.metadata.autonomy_level == "autonomous"