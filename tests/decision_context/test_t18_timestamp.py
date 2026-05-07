"""T18: Decision context has timestamp"""

import pytest
from identity_agent import identity_agent_service


def test_identity_context_timestamp(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]
    result = identity_agent_service(payload, mock_db_active)

    assert result.identity_context.timestamp is not None