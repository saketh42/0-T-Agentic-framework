"""T22: Null database client returns error"""

import pytest
from identity_agent import identity_agent_service


def test_null_db_client(test_inputs):
    payload = test_inputs["valid_request"]
    result = identity_agent_service(payload, db_client=None)

    assert result.is_authorized is False
    assert "database" in result.failure_reason.lower()