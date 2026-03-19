CREATE TABLE IF NOT EXISTS agent_registry (
  agent_id TEXT PRIMARY KEY,
  role TEXT NOT NULL,
  risk_tier TEXT NOT NULL,
  autonomy_level TEXT NOT NULL,
  capabilities TEXT[] NOT NULL,
  allowed_tools TEXT[] NOT NULL,
  status TEXT NOT NULL,
  owner TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  origin TEXT NOT NULL,
  network_zone TEXT NOT NULL
);

INSERT INTO agent_registry (
  agent_id,
  role,
  risk_tier,
  autonomy_level,
  capabilities,
  allowed_tools,
  status,
  owner,
  tenant_id,
  origin,
  network_zone
)
VALUES
  (
    'triage-agent',
    'SOC_AGENT',
    'tier2',
    'medium',
    ARRAY['investigation', 'triage'],
    ARRAY['siem_query', 'threat_intel'],
    'active',
    'SOC Platform',
    'tenant-acme',
    'soc-copilot-ui',
    'internal'
  ),
  (
    'containment-agent',
    'IR_AGENT',
    'tier3',
    'high',
    ARRAY['containment', 'response'],
    ARRAY['isolate_host'],
    'active',
    'IR Team',
    'tenant-acme',
    'ir-console',
    'internal'
  ),
  (
    'blocked-agent',
    'SOC_AGENT',
    'tier2',
    'medium',
    ARRAY['investigation'],
    ARRAY['siem_query'],
    'suspended',
    'SOC Platform',
    'tenant-acme',
    'soc-copilot-ui',
    'restricted'
  )
ON CONFLICT (agent_id) DO UPDATE SET
  role = EXCLUDED.role,
  risk_tier = EXCLUDED.risk_tier,
  autonomy_level = EXCLUDED.autonomy_level,
  capabilities = EXCLUDED.capabilities,
  allowed_tools = EXCLUDED.allowed_tools,
  status = EXCLUDED.status,
  owner = EXCLUDED.owner,
  tenant_id = EXCLUDED.tenant_id,
  origin = EXCLUDED.origin,
  network_zone = EXCLUDED.network_zone;
