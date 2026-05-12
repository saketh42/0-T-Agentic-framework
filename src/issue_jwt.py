"""
Issue JWT for Identity Agent

Signs a JWT attesting to the agent's verified identity
using RS256 with the Identity Service's private key.
"""

import os
import jwt
from datetime import datetime, timedelta, timezone
from schemas import AgentIdentityDecisionContext


def _load_private_key() -> str:
    key_path = os.getenv("IDENTITY_PRIVATE_KEY_PATH")
    if key_path:
        with open(key_path) as f:
            return f.read()
    key = os.getenv("IDENTITY_PRIVATE_KEY")
    if key:
        return key
    msg = (
        "IDENTITY_PRIVATE_KEY_PATH or IDENTITY_PRIVATE_KEY "
        "environment variable must be set"
    )
    raise RuntimeError(msg)


def issue_agent_jwt(context: AgentIdentityDecisionContext, ttl_minutes: int = 60) -> str:
    private_key = _load_private_key()
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=ttl_minutes)
    payload = {
        "sub": context.agent_id,
        "tenant_id": context.tenant_id,
        "session_id": context.session_id,
        "environment": context.environment,
        "network_zone": context.network_zone,
        "origin": context.origin,
        "role": context.metadata.role,
        "risk_tier": context.metadata.risk_tier,
        "autonomy_level": context.metadata.autonomy_level,
        "allowed_tools": context.metadata.allowed_tools,
        "capabilities": context.metadata.capabilities,
        "governance_tags": context.metadata.governance_tags,
        "iss": "identity-agent",
        "iat": now,
        "exp": expires_at,
    }
    token = jwt.encode(payload, private_key, algorithm="RS256")
    return token
