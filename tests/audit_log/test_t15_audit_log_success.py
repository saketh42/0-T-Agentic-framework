"""T15: For success, decision context sent to Gateway (no audit log)"""

import pytest
from identity_agent import identity_agent_service


def test_audit_log_on_success(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]
    result = identity_agent_service(payload, mock_db_active)

    # For success, we send to Gateway - no audit log
    assert result.is_authorized is True
    assert result.identity_context is not None