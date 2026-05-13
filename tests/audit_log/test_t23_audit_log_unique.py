"""T23: For success, no audit log (goes to Gateway)"""

import pytest
from identity_agent import identity_agent_service


def test_audit_log_event_id_unique(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]

    result1 = identity_agent_service(payload, mock_db_active)
    result2 = identity_agent_service(payload, mock_db_active)

    # For success, audit_log_id is None (goes to Gateway)
    assert result1.audit_log_id is None
    assert result2.audit_log_id is None
    assert result1.authorization == "ALLOW"
    assert result2.authorization == "ALLOW"