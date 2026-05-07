"""T07: Invalid JSON payload"""

import pytest
from identity_agent import identity_agent_service


def test_invalid_json_payload(test_inputs, mock_db_active):
    result = identity_agent_service("not valid json", mock_db_active)

    assert result.is_authorized is False
    assert "invalid" in result.failure_reason.lower()