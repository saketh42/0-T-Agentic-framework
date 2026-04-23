"""T18: Decision context has timestamp"""

import pytest
from core.identity_agent import identity_agent_flow


def test_decision_context_timestamp(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]
    result = identity_agent_flow(payload, mock_db_active)

    assert result.decision_context.timestamp is not None