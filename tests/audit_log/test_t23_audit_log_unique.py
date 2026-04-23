"""T23: Audit log event_id is unique per request"""

import pytest
from core.identity_agent import identity_agent_flow


def test_audit_log_event_id_unique(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]

    result1 = identity_agent_flow(payload, mock_db_active)
    result2 = identity_agent_flow(payload, mock_db_active)

    assert result1.audit_event_id is not None
    assert result2.audit_event_id is not None
    assert result1.audit_event_id != result2.audit_event_id