"""T10: Cross-environment access denied"""

import pytest
from conftest import create_mock_db_with_record
from identity_agent import identity_agent_flow


def test_cross_environment(test_inputs, cross_environment_record):
    mock_db = create_mock_db_with_record(cross_environment_record)

    payload = test_inputs["cross_environment"]
    result = identity_agent_flow(payload, mock_db)

    assert result.success is False
    assert "cross-environment" in result.error_message.lower()