"""T14: Missing metadata returns error"""

import pytest
from core.identity_agent import identity_agent_flow


def test_missing_metadata(test_inputs, mock_db_active_no_metadata):
    payload = test_inputs["missing_metadata"]
    result = identity_agent_flow(payload, mock_db_active_no_metadata)

    assert result.success is False
    assert "missing metadata" in result.error_message.lower()