-- Signing keys table for JWT key management
CREATE TABLE IF NOT EXISTS signing_keys (
    kid TEXT PRIMARY KEY,
    private_key_pem TEXT NOT NULL,
    public_key_pem TEXT NOT NULL,
    algorithm TEXT DEFAULT 'RS256',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_signing_keys_active ON signing_keys(active);
CREATE INDEX IF NOT EXISTS idx_signing_keys_expires ON signing_keys(expires_at);
