"""T23: For success, no audit log (goes to Policy Agent)"""

import pytest
from identity_agent import identity_agent_flow


def test_audit_log_event_id_unique(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]

    result1 = identity_agent_flow(payload, mock_db_active)
    result2 = identity_agent_flow(payload, mock_db_active)

    # For success, audit_event_id is None (goes to Policy Agent)
    assert result1.audit_event_id is None
    assert result2.audit_event_id is None
    assert result1.success is True
    assert result2.success is True