# JWT Key Management

## Overview

The Identity Agent issues RS256-signed JWTs to attest to an agent's verified identity. The signing keys are stored in a `signing_keys` table in PostgreSQL. The corresponding public keys are served via a JWKS endpoint so that agents and the Gateway can verify the JWT signatures.

---

## Key Generation

Use the `generate_key.py` CLI to generate a new RSA 2048-bit key pair and insert it into the `signing_keys` table:

```bash
python3 src/generate_key.py --days 365
```

This does the following:

1. Generates an RSA 2048-bit private key
2. Derives the public key
3. Computes `kid` = SHA-256 thumbprint of the public key (RFC 7638)
4. Inserts the key into `signing_keys` with `active=true` and the specified expiry

The `signing_keys.sql` file defines the table schema:

```sql
CREATE TABLE signing_keys (
    kid TEXT PRIMARY KEY,
    private_key_pem TEXT NOT NULL,
    public_key_pem TEXT NOT NULL,
    algorithm TEXT DEFAULT 'RS256',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ
);
```

---

## Key Storage

Keys are stored in the `signing_keys` table:

| Column | Description |
|--------|-------------|
| `kid` | Key ID (SHA-256 fingerprint of public key) |
| `private_key_pem` | PKCS#8 RSA private key (PEM) |
| `public_key_pem` | SubjectPublicKeyInfo RSA public key (PEM) |
| `algorithm` | Signing algorithm (RS256) |
| `active` | Whether the key is active for signing |
| `created_at` | Key creation timestamp |
| `expires_at` | Key expiration (null = no expiry) |

Multiple keys can coexist. `get_active_signing_key()` returns the most recently created active, non-expired key.

---

## JWT Issuance Flow

```
identity_agent_service()
  │
  ├── Step 1-5: Validate, lookup, fetch metadata, build context
  │
  ├── issue_agent_jwt(decision_context, db_client)
  │     │
  │     ├── db_client.get_active_signing_key()  →  (private_key, kid)
  │     │     (falls back to IDENTITY_PRIVATE_KEY_PATH env var,
  │     │      IDENTITY_PRIVATE_KEY env var, or test key file)
  │     │
  │     ├── Build payload: { sub, iss, iat, exp }
  │     │
  │     └── jwt.encode(payload, private_key, RS256, { kid })
  │
  └── decision_context.token = <JWT>
```

### JWT Header

```json
{
  "alg": "RS256",
  "kid": "abc123def456..."
}
```

### JWT Payload

```json
{
  "sub": "agent-001",
  "iss": "identity-agent",
  "iat": 1714000000,
  "exp": 1714003600
}
```

The JWT contains only standard claims. Agent attributes (role, risk tier, allowed tools, etc.) are in the `AgentIdentityDecisionContext` returned alongside the JWT, not embedded in the token. This keeps the JWT compact and ensures attribute changes don't require token re-issuance.

---

## JWKS Endpoint

The `GET /.well-known/jwks.json` endpoint serves the public keys for JWT verification.

### Without Filtering

```
GET /.well-known/jwks.json
```

Returns all active, non-expired signing keys:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "n": "<base64url-modulus>",
      "e": "<base64url-exponent>",
      "use": "sig",
      "alg": "RS256",
      "kid": "abc123def456..."
    }
  ]
}
```

### With kid Filtering

```
GET /.well-known/jwks.json?kid=abc123def456...
```

Returns only the key matching the given `kid`:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "n": "<base64url-modulus>",
      "e": "<base64url-exponent>",
      "use": "sig",
      "alg": "RS256",
      "kid": "abc123def456..."
    }
  ]
}
```

If no key matches the `kid`, an empty list is returned.

---

## Agent Verification Flow

When an agent receives a JWT from the Identity Agent, it verifies it as follows:

```
1. Extract kid from JWT header
         │
2. GET /.well-known/jwks.json?kid=<kid>
         │
3. Find matching JWK entry (n, e)
         │
4. Verify JWT signature:
   - Decode JWT with RS256 using (n, e)
   - Check iss == "identity-agent"
   - Check sub matches expected agent_id
   - Check exp > now
```

The trust model relies on:
- **HTTPS** on the JWKS endpoint (prevents MITM tampering)
- **DB access controls** on the `signing_keys` table (prevents unauthorized key writes)
- **kid matching** between the JWT header and the JWKS entry

---

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `IDENTITY_PRIVATE_KEY_PATH` | Path to PEM private key file (fallback when no DB) | none |
| `IDENTITY_PRIVATE_KEY` | PEM private key as string (fallback when no DB and no path) | none |

Without DB or fallback, the system looks for `tests/test_data/test_jwt_private.pem`.

---

## Key Rotation

To rotate keys:

1. Generate a new key: `python3 src/generate_key.py --days 365`
2. The old key remains in `signing_keys` (active until expiry) so existing JWTs can still be verified
3. New JWTs are signed with the newest key (by `created_at DESC`)
4. JWKS endpoint returns both keys, so verifiers can validate JWTs signed with either key
5. Once all JWTs signed with the old key expire, deactivate the old key or let it expire naturally
