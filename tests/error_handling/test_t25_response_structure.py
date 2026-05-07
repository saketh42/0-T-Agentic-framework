"""T25: IdentityValidationResponse has correct structure"""

import pytest
from identity_agent import identity_agent_service


def test_response_structure_success(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]
    result = identity_agent_service(payload, mock_db_active)

    assert result.identity_context is not None
    assert result.audit_log_id is None  # Success goes to Gateway, no audit log
    assert result.failure_reason is None


def test_response_structure_failure(test_inputs, mock_db_suspended):
    payload = test_inputs["suspended_agent"]
    result = identity_agent_service(payload, mock_db_suspended)

    assert result.identity_context is None
    assert result.failure_reason is not None
    assert result.audit_log_id is not None  # Failure writes to audit log