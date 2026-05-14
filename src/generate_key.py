"""
Generate a new RSA signing key pair and store it in the signing_keys table.

Usage:
    python3 src/generate_key.py [--days 30]
"""

import sys
import os
import argparse
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from schemas import SigningKey
from postgres_client import PostgresIdentityAgentDatabaseClient
from issue_jwt import _fingerprint


def generate_key(days_valid: int = 365):
    db = PostgresIdentityAgentDatabaseClient()

    # Generate RSA 2048 key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    kid = _fingerprint(public_pem)
    now = datetime.now(timezone.utc)

    signing_key = SigningKey(
        kid=kid,
        private_key_pem=private_pem,
        public_key_pem=public_pem,
        algorithm="RS256",
        active=True,
        created_at=now,
        expires_at=now + timedelta(days=days_valid),
    )

    db.insert_signing_key(signing_key)
    db.close()

    print(f"Generated signing key:")
    print(f"  kid: {kid}")
    print(f"  algorithm: RS256")
    print(f"  expires: {signing_key.expires_at}")
    print(f"  public_key: {public_pem[:60]}...")
    return signing_key


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=365, help="Days until key expires")
    args = parser.parse_args()
    generate_key(args.days)
