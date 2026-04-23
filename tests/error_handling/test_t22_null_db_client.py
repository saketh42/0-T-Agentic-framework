"""T22: Null database client returns error"""

import pytest
from core.identity_agent import identity_agent_flow


def test_null_db_client(test_inputs):
    payload = test_inputs["valid_request"]
    result = identity_agent_flow(payload, db_client=None)

    assert result.success is False
    assert "database" in result.error_message.lower()