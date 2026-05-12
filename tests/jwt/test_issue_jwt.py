"""Tests for JWT issuance in Identity Agent"""

import os
import sys
import json
import jwt as pyjwt
from datetime import datetime

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from schemas import AgentIdentityDecisionContext, AgentSecurityMetadata
from issue_jwt import issue_agent_jwt, _load_private_key

TEST_KEY_PATH = os.path.join(
    os.path.dirname(__file__), "..", "test_data", "test_jwt_private.pem"
)
TEST_PUBLIC_KEY_PATH = os.path.join(
    os.path.dirname(__file__), "..", "test_data", "test_jwt_public.pem"
)


@pytest.fixture(scope="session", autouse=True)
def setup_env():
    os.environ["IDENTITY_PRIVATE_KEY_PATH"] = TEST_KEY_PATH
    yield
    del os.environ["IDENTITY_PRIVATE_KEY_PATH"]


@pytest.fixture
def decision_context():
    metadata = AgentSecurityMetadata(
        agent_id="agent-001",
        name="Test Agent",
        role="planner",
        risk_tier="medium",
        autonomy_level="supervised",
        allowed_tools=["siem_query", "edr_lookup"],
        capabilities=["threat_hunting", "enrichment"],
        governance_tags=["pci", "hipaa"],
        updated_at=datetime.utcnow(),
    )
    return AgentIdentityDecisionContext(
        agent_id="agent-001",
        tenant_id="tenant-acme",
        environment="prod",
        network_zone="dmz",
        origin="192.168.1.100",
        session_id="sess-123",
        metadata=metadata,
        status="active",
        timestamp=datetime.utcnow(),
    )


def test_issue_jwt_returns_string(decision_context):
    token = issue_agent_jwt(decision_context)
    assert isinstance(token, str)
    assert len(token) > 0


def test_issue_jwt_decodes_with_public_key(decision_context):
    token = issue_agent_jwt(decision_context)
    with open(TEST_PUBLIC_KEY_PATH) as f:
        public_key = f.read()
    decoded = pyjwt.decode(token, public_key, algorithms=["RS256"])
    assert decoded["sub"] == "agent-001"
    assert decoded["tenant_id"] == "tenant-acme"
    assert decoded["session_id"] == "sess-123"
    assert decoded["environment"] == "prod"
    assert decoded["network_zone"] == "dmz"
    assert decoded["origin"] == "192.168.1.100"
    assert decoded["role"] == "planner"
    assert decoded["risk_tier"] == "medium"
    assert decoded["autonomy_level"] == "supervised"
    assert decoded["allowed_tools"] == ["siem_query", "edr_lookup"]
    assert decoded["capabilities"] == ["threat_hunting", "enrichment"]
    assert decoded["governance_tags"] == ["pci", "hipaa"]


def test_issue_jwt_issuer_is_identity_agent(decision_context):
    token = issue_agent_jwt(decision_context)
    with open(TEST_PUBLIC_KEY_PATH) as f:
        public_key = f.read()
    decoded = pyjwt.decode(token, public_key, algorithms=["RS256"])
    assert decoded["iss"] == "identity-agent"


def test_issue_jwt_has_timestamps(decision_context):
    token = issue_agent_jwt(decision_context)
    with open(TEST_PUBLIC_KEY_PATH) as f:
        public_key = f.read()
    decoded = pyjwt.decode(token, public_key, algorithms=["RS256"])
    assert "iat" in decoded
    assert "exp" in decoded
    assert decoded["exp"] > decoded["iat"]


def test_issue_jwt_default_ttl_is_60_minutes(decision_context):
    token = issue_agent_jwt(decision_context)
    with open(TEST_PUBLIC_KEY_PATH) as f:
        public_key = f.read()
    decoded = pyjwt.decode(token, public_key, algorithms=["RS256"])
    ttl_seconds = decoded["exp"] - decoded["iat"]
    assert ttl_seconds == 3600


def test_issue_jwt_custom_ttl(decision_context):
    token = issue_agent_jwt(decision_context, ttl_minutes=30)
    with open(TEST_PUBLIC_KEY_PATH) as f:
        public_key = f.read()
    decoded = pyjwt.decode(token, public_key, algorithms=["RS256"])
    ttl_seconds = decoded["exp"] - decoded["iat"]
    assert ttl_seconds == 1800


def test_issue_jwt_different_agents(decision_context):
    token1 = issue_agent_jwt(decision_context)
    metadata2 = AgentSecurityMetadata(
        agent_id="agent-002",
        name="Other Agent",
        role="worker",
        risk_tier="low",
        autonomy_level="autonomous",
        allowed_tools=["ticket_create"],
        capabilities=["reporting"],
        governance_tags=["sox"],
        updated_at=datetime.utcnow(),
    )
    ctx2 = AgentIdentityDecisionContext(
        agent_id="agent-002",
        tenant_id="tenant-acme",
        environment="staging",
        network_zone="internal",
        origin="10.0.0.1",
        session_id="sess-456",
        metadata=metadata2,
        status="active",
        timestamp=datetime.utcnow(),
    )
    token2 = issue_agent_jwt(ctx2)
    assert token1 != token2
    with open(TEST_PUBLIC_KEY_PATH) as f:
        public_key = f.read()
    decoded2 = pyjwt.decode(token2, public_key, algorithms=["RS256"])
    assert decoded2["sub"] == "agent-002"
    assert decoded2["environment"] == "staging"


def test_issue_jwt_invalid_signature_rejected(decision_context):
    token = issue_agent_jwt(decision_context)
    with open(TEST_PUBLIC_KEY_PATH) as f:
        public_key = f.read()
    decoded = pyjwt.decode(token, public_key, algorithms=["RS256"])
    tampered = token.rsplit(".", 1)[0] + ".invalidsignature"
    with pytest.raises(pyjwt.exceptions.InvalidSignatureError):
        pyjwt.decode(tampered, public_key, algorithms=["RS256"])


def test_load_private_key_from_env_var(decision_context, monkeypatch):
    monkeypatch.delenv("IDENTITY_PRIVATE_KEY_PATH", raising=False)
    with open(TEST_KEY_PATH) as f:
        key_content = f.read()
    monkeypatch.setenv("IDENTITY_PRIVATE_KEY", key_content)
    token = issue_agent_jwt(decision_context)
    assert isinstance(token, str)
    assert len(token) > 0


def test_load_private_key_missing_raises(monkeypatch, decision_context):
    monkeypatch.delenv("IDENTITY_PRIVATE_KEY_PATH", raising=False)
    monkeypatch.delenv("IDENTITY_PRIVATE_KEY", raising=False)
    with pytest.raises(RuntimeError, match="IDENTITY_PRIVATE_KEY"):
        issue_agent_jwt(decision_context)
