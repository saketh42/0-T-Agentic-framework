CREATE TABLE IF NOT EXISTS agents (
    agent_id TEXT PRIMARY KEY,
    tenant_id TEXT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    purpose TEXT,
    environment TEXT,
    role VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    risk_tier VARCHAR(20) DEFAULT 'low',
    autonomy_level INT CHECK (autonomy_level BETWEEN 1 AND 5),
    allowed_tools TEXT[] DEFAULT '{}',
    capabilities TEXT[] DEFAULT '{}',
    governance_tags TEXT[] DEFAULT '{}',
    ownership_team TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS signing_keys (
    kid TEXT PRIMARY KEY,
    private_key_pem TEXT NOT NULL,
    public_key_pem TEXT NOT NULL,
    algorithm TEXT NOT NULL DEFAULT 'RS256',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);
