"""T09: Cross-tenant access denied"""

import pytest
from conftest import create_mock_db_with_record
from identity_agent import identity_agent_service


def test_cross_tenant(test_inputs, cross_tenant_record):
    mock_db = create_mock_db_with_record(cross_tenant_record)

    payload = test_inputs["cross_tenant"]
    result = identity_agent_service(payload, mock_db)

    assert result.is_authorized is False
    assert "cross-tenant" in result.failure_reason.lower()