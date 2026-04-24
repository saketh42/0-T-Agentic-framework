"""T15: Audit log written on success"""

import pytest
from identity_agent import identity_agent_flow


def test_audit_log_on_success(test_inputs, mock_db_active):
    payload = test_inputs["valid_request"]
    result = identity_agent_flow(payload, mock_db_active)

    assert mock_db_active.write_audit_log.called is True

    audit_log = mock_db_active.write_audit_log.call_args[0][0]
    assert audit_log.decision == "ALLOW"