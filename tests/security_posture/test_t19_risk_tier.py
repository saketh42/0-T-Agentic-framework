"""T19: Security posture - risk_tier passed through"""

import pytest
from identity_agent import identity_agent_service


def test_security_posture_risk_tier(test_inputs, mock_db_high_risk):
    payload = test_inputs["high_risk_agent"]
    result = identity_agent_service(payload, mock_db_high_risk)

    assert result.is_authorized is True
    assert result.identity_context is not None

    assert result.identity_context.metadata.risk_tier == "critical"
    assert result.identity_context.metadata.autonomy_level == "execute"