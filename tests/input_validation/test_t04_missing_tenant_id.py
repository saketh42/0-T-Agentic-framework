"""T04: Missing tenant_id"""

import pytest
from identity_agent import identity_agent_service


def test_missing_tenant_id(test_inputs, mock_db_active):
    payload = test_inputs["missing_tenant_id"]
    result = identity_agent_service(payload, mock_db_active)

    assert result.authorization == "DENY"
    assert "tenant_id" in result.failure_reason.lower()