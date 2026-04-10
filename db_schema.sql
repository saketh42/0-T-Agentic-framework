CREATE TABLE agents (
    agent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    role VARCHAR(50),
    purpose TEXT,
    status VARCHAR(20), 
    risk_tier VARCHAR(20), 
    autonomy_level INT CHECK (autonomy_level BETWEEN 1 AND 5),
    governance_tags TEXT[],
    owner_team TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE tools (
    tool_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50), 
    sensitivity VARCHAR(20), 
    endpoint TEXT,
    environment TEXT,
    tenant_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_tools_name_tenant 
ON tools(name, tenant_id);

CREATE TABLE agent_tools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(agent_id) ON DELETE CASCADE,
    tool_id UUID REFERENCES tools(tool_id) ON DELETE CASCADE,
    allowed_actions TEXT[], 

    UNIQUE(agent_id, tool_id) 
);
CREATE TABLE policies (
    policy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    scope VARCHAR(50) NOT NULL, 
    rule JSONB NOT NULL,
    action VARCHAR(20) CHECK (action IN ('allow','deny','sanitize','escalate')),
    severity VARCHAR(20), 
    threat_tags TEXT[],
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE policy_targets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_id UUID REFERENCES policies(policy_id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(agent_id),
    role VARCHAR(50),
    tool_category VARCHAR(50),
    tenant_id TEXT
);
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(agent_id),
    tenant_id TEXT,
    session_id TEXT,
    environment TEXT,
    origin TEXT,
    network_zone TEXT,
    scope VARCHAR(50), 
    decision VARCHAR(20), 
    action TEXT,
    tool_id UUID,
    policy_ids TEXT[],
    reasons TEXT[],
    severity VARCHAR(20),
    request_id TEXT,
    trace_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hash TEXT,
    previous_hash TEXT,
    tamper_proof_ref TEXT
);

INSERT INTO agents (tenant_id, name, type, role, purpose, status, risk_tier, autonomy_level, governance_tags, owner_team)
VALUES (
    'tenant_1',
	'SecurityAgent',
    'Security',
    'monitor',
    'Monitor threats',
    'active',
    'high',
    3,
    ARRAY['critical','pii'],
    'SOC Team'
);
SELECT * FROM agents;
UPDATE agents
SET risk_tier = 'medium',
    status = 'inactive'
WHERE name = 'SecurityAgent';
UPDATE agents
SET risk_tier = 'medium',
    status = 'inactive'
WHERE name = 'SecurityAgent';


INSERT INTO tools (name, description, category, sensitivity, endpoint, environment, tenant_id)
VALUES (
    'FileTool',
    'Access files',
    'fs',
    'high',
    '/file-access',
    'prod',
    'tenant_1'
);
SELECT * FROM tools;
UPDATE tools
SET sensitivity = 'medium'
WHERE name = 'FileTool';
DELETE FROM tools
WHERE name = 'FileTool';


INSERT INTO agent_tools (agent_id, tool_id, allowed_actions)
VALUES (
    (SELECT agent_id FROM agents WHERE name='SecurityAgent'),
    (SELECT tool_id FROM tools WHERE name='FileTool'),
    ARRAY['read','write']
);
SELECT * FROM agent_tools;
UPDATE agent_tools
SET allowed_actions = ARRAY['read']
WHERE agent_id = (SELECT agent_id FROM agents WHERE name='SecurityAgent');
DELETE FROM agent_tools
WHERE agent_id = (SELECT agent_id FROM agents WHERE name='SecurityAgent');


INSERT INTO policies (name, scope, rule, action, severity, threat_tags)
VALUES (
    'Block File Access',
    'check_tool_call',
    '{"tool_category":"fs","risk":"high"}',
    'deny',
    'high',
    ARRAY['T4','ASI02']
);
SELECT * FROM policies;
UPDATE policies
SET enabled = FALSE
WHERE name = 'Block File Access';
DELETE FROM policies
WHERE name = 'Block File Access';


INSERT INTO policy_targets (policy_id, agent_id, role, tool_category, tenant_id)
VALUES (
    (SELECT policy_id FROM policies WHERE name='Block File Access'),
    (SELECT agent_id FROM agents WHERE name='SecurityAgent'),
    'monitor',
    'fs',
    'tenant_1'
);
SELECT * FROM policy_targets;
UPDATE policy_targets
SET role = 'admin'
WHERE tenant_id = 'tenant_1';
DELETE FROM policy_targets
WHERE tenant_id = 'tenant_1';


INSERT INTO audit_logs (
    agent_id, tenant_id, session_id, environment,
    origin, network_zone, scope, decision, action,
    tool_id, policy_ids, reasons, severity,
    request_id, trace_id, hash, previous_hash
)
VALUES (
    (SELECT agent_id FROM agents WHERE name='SecurityAgent'),
    'tenant_1',
    'session_123',
    'prod',
    'api',
    'internal',
    'check_tool_call',
    'deny',
    'Blocked file access',
    (SELECT tool_id FROM tools WHERE name='FileTool'),
    ARRAY['policy_1'],
    ARRAY['High risk detected'],
    'high',
    'req_001',
    'trace_001',
    'hash123',
    'prevhash123'
);
SELECT * FROM audit_logs;