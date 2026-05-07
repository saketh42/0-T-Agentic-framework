"""T14: Missing metadata returns error"""

import pytest
from identity_agent import identity_agent_service


def test_missing_metadata(test_inputs, mock_db_active_no_metadata):
    payload = test_inputs["missing_metadata"]
    result = identity_agent_service(payload, mock_db_active_no_metadata)

    assert result.is_authorized is False
    assert "missing metadata" in result.failure_reason.lower()