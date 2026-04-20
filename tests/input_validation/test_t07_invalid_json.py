"""T07: Invalid JSON payload"""

import pytest
from identity_agent import identity_agent_flow


def test_invalid_json_payload(test_inputs, mock_db_active):
    result = identity_agent_flow("not valid json", mock_db_active)

    assert result.success is False
    assert "invalid" in result.error_message.lower()