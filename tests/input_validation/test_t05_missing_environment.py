"""T05: Missing environment"""

import pytest
from core.identity_agent import identity_agent_flow


def test_missing_environment(test_inputs, mock_db_active):
    payload = test_inputs["missing_environment"]
    result = identity_agent_flow(payload, mock_db_active)

    assert result.success is False
    assert "environment" in result.error_message.lower()