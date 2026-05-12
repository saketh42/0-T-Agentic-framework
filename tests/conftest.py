"""Shared pytest fixtures for Identity Agent tests"""

import sys
import os
import json
from datetime import datetime
from unittest.mock import Mock

import pytest

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")


@pytest.fixture(scope="session", autouse=True)
def setup_jwt_key():
    key_path = os.path.join(TEST_DATA_DIR, "test_jwt_private.pem")
    os.environ["IDENTITY_PRIVATE_KEY_PATH"] = key_path
    yield
    os.environ.pop("IDENTITY_PRIVATE_KEY_PATH", None)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from schemas import (
    AgentRegistryRecord,
    AgentSecurityMetadata,
)
from database import IdentityAgentDatabaseClient
from identity_agent import identity_agent_service


def load_json(filename):
    path = os.path.join(TEST_DATA_DIR, filename)
    with open(path, 'r') as f:
        return json.load(f)


MOCK_DATA = load_json("identity_agent_mocks.json")
TEST_INPUTS = load_json("identity_agent_inputs.json")["requests"]


@pytest.fixture(scope="session")
def test_inputs():
    return TEST_INPUTS


@pytest.fixture(scope="session")
def mock_data():
    return MOCK_DATA


def parse_dt(dt_str):
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))


def create_registry_record(data):
    return AgentRegistryRecord(
        agent_id=data["agent_id"],
        tenant_id=data["tenant_id"],
        name=data.get("name", "Test Agent"),
        type=data.get("type"),
        purpose=data.get("purpose"),
        role=data.get("role"),
        status=data.get("status", "active"),
        risk_tier=data.get("risk_tier"),
        autonomy_level=data.get("autonomy_level"),
        ownership_team=data.get("ownership_team"),
        governance_tags=data.get("governance_tags", []),
        created_at=parse_dt(data.get("created_at", "2024-01-01T00:00:00Z")),
        updated_at=parse_dt(data.get("updated_at", "2024-01-01T00:00:00Z"))
    )


def create_metadata(agent_id, data):
    return AgentSecurityMetadata(
        agent_id=agent_id,
        name=data.get("name", "Test Agent"),
        role=data["role"],
        risk_tier=data["risk_tier"],
        autonomy_level=data["autonomy_level"],
        allowed_tools=data["allowed_tools"],
        capabilities=data["capabilities"],
        governance_tags=data["governance_tags"],
        updated_at=parse_dt(data["updated_at"])
    )


def create_mock_db(agent_id, status, has_metadata=True):
    mock = Mock(spec=IdentityAgentDatabaseClient)
    mock.fetch_from_registry_active = Mock(return_value=None)
    mock.fetch_from_registry_suspended = Mock(return_value=None)
    mock.fetch_from_registry_disabled = Mock(return_value=None)
    mock.fetch_from_registry_pending = Mock(return_value=None)
    mock.fetch_agent_security_metadata = Mock(return_value=None)
    mock.write_audit_log = Mock(return_value=True)

    registry_data = MOCK_DATA["registry_records"].get(agent_id, {}).get(status)
    if registry_data:
        record = create_registry_record(registry_data)
        if status == "active":
            mock.fetch_from_registry_active.return_value = record
        elif status == "suspended":
            mock.fetch_from_registry_suspended.return_value = record
        elif status == "disabled":
            mock.fetch_from_registry_disabled.return_value = record
        elif status == "pending":
            mock.fetch_from_registry_pending.return_value = record

    if has_metadata:
        metadata_data = MOCK_DATA["metadata"].get(agent_id)
        if metadata_data:
            mock.fetch_agent_security_metadata.return_value = create_metadata(agent_id, metadata_data)

    return mock


def create_mock_db_for_unknown():
    mock = Mock(spec=IdentityAgentDatabaseClient)
    mock.fetch_from_registry_active = Mock(return_value=None)
    mock.fetch_from_registry_suspended = Mock(return_value=None)
    mock.fetch_from_registry_disabled = Mock(return_value=None)
    mock.fetch_from_registry_pending = Mock(return_value=None)
    mock.fetch_agent_security_metadata = Mock(return_value=None)
    mock.write_audit_log = Mock(return_value=True)
    return mock


def create_mock_db_with_record(record, has_metadata=True):
    mock = Mock(spec=IdentityAgentDatabaseClient)
    mock.fetch_from_registry_active = Mock(return_value=None)
    mock.fetch_from_registry_suspended = Mock(return_value=None)
    mock.fetch_from_registry_disabled = Mock(return_value=None)
    mock.fetch_from_registry_pending = Mock(return_value=None)
    mock.fetch_agent_security_metadata = Mock(return_value=None)
    mock.write_audit_log = Mock(return_value=True)

    if record:
        mock.fetch_from_registry_active.return_value = record

    if has_metadata:
        metadata_data = MOCK_DATA["metadata"].get(record.agent_id)
        if metadata_data:
            mock.fetch_agent_security_metadata.return_value = create_metadata(record.agent_id, metadata_data)

    return mock


@pytest.fixture
def mock_db_active(test_inputs):
    return create_mock_db("agent-001", "active")


@pytest.fixture
def mock_db_suspended(test_inputs):
    return create_mock_db("agent-001", "suspended")


@pytest.fixture
def mock_db_disabled(test_inputs):
    return create_mock_db("agent-001", "disabled")


@pytest.fixture
def mock_db_pending(test_inputs):
    return create_mock_db("agent-001", "pending")


@pytest.fixture
def mock_db_active_no_metadata(test_inputs):
    return create_mock_db("agent-001", "active", has_metadata=False)


@pytest.fixture
def mock_db_high_risk(test_inputs):
    return create_mock_db("agent-highrisk", "active")


@pytest.fixture
def mock_db_unknown():
    return create_mock_db_for_unknown()


@pytest.fixture
def cross_tenant_record():
    return create_registry_record(MOCK_DATA["cross_tenant_record"])


@pytest.fixture
def cross_environment_record():
    return create_registry_record(MOCK_DATA["cross_environment_record"])