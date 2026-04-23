"""T09: Cross-tenant access denied"""

import pytest
from conftest import create_mock_db_with_record
from core.identity_agent import identity_agent_flow


def test_cross_tenant(test_inputs, cross_tenant_record):
    mock_db = create_mock_db_with_record(cross_tenant_record)

    payload = test_inputs["cross_tenant"]
    result = identity_agent_flow(payload, mock_db)

    assert result.success is False
    assert "cross-tenant" in result.error_message.lower()