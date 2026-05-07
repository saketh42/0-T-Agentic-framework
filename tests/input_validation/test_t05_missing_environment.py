"""T05: Missing environment"""

import pytest
from identity_agent import identity_agent_service


def test_missing_environment(test_inputs, mock_db_active):
    payload = test_inputs["missing_environment"]
    result = identity_agent_service(payload, mock_db_active)

    assert result.is_authorized is False
    assert "environment" in result.failure_reason.lower()