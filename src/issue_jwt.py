"""
Issue JWT for Identity Agent

Signs a JWT attesting to the agent's verified identity
using RS256 with keys loaded from the signing_keys table.
"""

import os
import hashlib
import base64
from typing import Optional, Tuple
import jwt
from datetime import datetime, timedelta, timezone
from schemas import AgentIdentityDecisionContext, SigningKey


def _fingerprint(public_key_pem: str) -> str:
    """Compute SHA-256 thumbprint of the public key per RFC 7638."""
    b64data = "".join(
        line.strip()
        for line in public_key_pem.splitlines()
        if line.strip() and not line.startswith("-----")
    )
    der = base64.b64decode(b64data)
    return base64.urlsafe_b64encode(hashlib.sha256(der).digest()).rstrip(b"=").decode()


def pem_to_jwk(public_key_pem: str) -> dict:
    """Convert a PEM public key to a JWK dict."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend

    pub = serialization.load_pem_public_key(public_key_pem.encode(), backend=default_backend())
    nums = pub.public_numbers()

    def _b64(n):
        length = (n.bit_length() + 7) // 8
        raw = n.to_bytes(length, byteorder="big")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    return {
        "kty": "RSA",
        "n": _b64(nums.n),
        "e": _b64(nums.e),
    }


def issue_agent_jwt(
    context: AgentIdentityDecisionContext,
    db_client=None,
    ttl_minutes: int = 60
) -> str:
    if db_client:
        key = db_client.get_active_signing_key()
    else:
        key = None

    if key is None:
        key = _load_key_from_fallback()

    private_key = key.private_key_pem
    kid = key.kid

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=ttl_minutes)
    payload = {
        "sub": context.agent_id,
        "iss": "identity-agent",
        "iat": now,
        "exp": expires_at,
    }
    headers = {"kid": kid}
    token = jwt.encode(payload, private_key, algorithm="RS256", headers=headers)
    return token


def _load_private_key() -> str:
    """Load the private key PEM string from env or fallback paths."""
    key_path = os.getenv("IDENTITY_PRIVATE_KEY_PATH")
    if key_path:
        with open(key_path) as f:
            return f.read()
    key = os.getenv("IDENTITY_PRIVATE_KEY")
    if key:
        return key
    for candidate in ["tests/test_data/test_jwt_private.pem", "tests\\test_data\\test_jwt_private.pem"]:
        if os.path.exists(candidate):
            with open(candidate) as f:
                return f.read()
    raise RuntimeError("IDENTITY_PRIVATE_KEY_PATH or IDENTITY_PRIVATE_KEY must be set")


def _load_key_from_fallback() -> SigningKey:
    """Fallback: load key from file/env when no DB is available."""
    key_path = os.getenv("IDENTITY_PRIVATE_KEY_PATH")
    if key_path:
        with open(key_path) as f:
            private_pem = f.read()
    else:
        key = os.getenv("IDENTITY_PRIVATE_KEY")
        if key:
            private_pem = key
        else:
            for candidate in ["tests/test_data/test_jwt_private.pem", "tests\\test_data\\test_jwt_private.pem"]:
                if os.path.exists(candidate):
                    with open(candidate) as f:
                        private_pem = f.read()
                    break
            else:
                raise RuntimeError("IDENTITY_PRIVATE_KEY_PATH or IDENTITY_PRIVATE_KEY must be set (no DB)")

    # Derive public key
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend

    priv = serialization.load_pem_private_key(
        private_pem.encode() if isinstance(private_pem, str) else private_pem,
        password=None,
        backend=default_backend()
    )
    pub = priv.public_key()
    public_pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    kid = _fingerprint(public_pem)

    return SigningKey(
        kid=kid,
        private_key_pem=private_pem,
        public_key_pem=public_pem,
        algorithm="RS256",
        active=True,
        created_at=datetime.now(timezone.utc),
    )


def validate_existing_jwt(
    token: str,
    expected_agent_id: str,
    db_client=None,
) -> Optional[str]:
    """Validate an existing JWT and return it if valid, None otherwise."""
    try:
        if db_client:
            key = db_client.get_active_signing_key()
        else:
            key = None

        if key is None:
            key = _load_key_from_fallback()

        public_key = key.public_key_pem

        claims = jwt.decode(token, public_key, algorithms=["RS256"])

        sub = claims.get("sub")
        if not sub or str(sub).strip() != str(expected_agent_id).strip():
            return None

        return token
    except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError, jwt.DecodeError, Exception):
        return None
