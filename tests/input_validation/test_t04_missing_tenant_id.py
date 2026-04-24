"""T04: Missing tenant_id"""

import pytest
from identity_agent import identity_agent_flow


def test_missing_tenant_id(test_inputs, mock_db_active):
    payload = test_inputs["missing_tenant_id"]
    result = identity_agent_flow(payload, mock_db_active)

    assert result.success is False
    assert "tenant_id" in result.error_message.lower()