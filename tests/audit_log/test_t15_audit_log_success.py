"""T15: For success, decision context sent to Policy Agent (no audit log)"""

import pytest
from identity_agent import identity_agent_flow


def test_audit_log_on_success(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]
    result = identity_agent_flow(payload, mock_db_active)

    # For success, we send to Policy Agent - no audit log
    assert result.success is True
    assert result.decision_context is not None