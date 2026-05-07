"""T16: Audit log written on denial"""

import pytest
from identity_agent import identity_agent_service


def test_audit_log_on_denial(test_inputs, mock_db_suspended):
    payload = test_inputs["suspended_agent"]
    result = identity_agent_service(payload, mock_db_suspended)

    assert mock_db_suspended.write_audit_log.called is True

    audit_log = mock_db_suspended.write_audit_log.call_args[0][0]
    assert audit_log.decision == "DENY"