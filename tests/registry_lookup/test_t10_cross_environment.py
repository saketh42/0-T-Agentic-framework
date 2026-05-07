"""T10: Cross-environment - no longer enforced (environment removed from schema)"""

import pytest
from conftest import create_mock_db_with_record
from identity_agent import identity_agent_service


def test_cross_environment(test_inputs, cross_environment_record):
    mock_db = create_mock_db_with_record(cross_environment_record)

    payload = test_inputs["cross_environment"]
    result = identity_agent_service(payload, mock_db)

    assert result.is_authorized is True