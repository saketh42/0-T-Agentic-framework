-- Identity Agent Database Schema
-- Single table for agents

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE agents (
    agent_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    environment TEXT NOT NULL,
    ownership_team TEXT,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK (status IN ('active', 'suspended', 'disabled', 'pending')),
    role TEXT,
    risk_tier TEXT CHECK (risk_tier IN ('low', 'medium', 'high', 'critical')),
    autonomy_level TEXT CHECK (autonomy_level IN ('supervised', 'autonomous')),
    allowed_tools TEXT[],
    capabilities TEXT[],
    governance_tags TEXT[]
);

CREATE INDEX idx_agents_tenant ON agents(tenant_id);
CREATE INDEX idx_agents_environment ON agents(environment);
CREATE INDEX idx_agents_status ON agents(status);

-- Audit logs table
CREATE TABLE audit_logs (
    log_id TEXT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    agent_id TEXT NOT NULL,
    session_id TEXT,
    tenant_id TEXT,
    environment TEXT,
    origin TEXT,
    network_zone TEXT,
    event_type TEXT,
    decision TEXT,
    reason TEXT
);

CREATE INDEX idx_audit_logs_agent ON audit_logs(agent_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);

-- Insert test data
INSERT INTO agents (agent_id, tenant_id, environment, ownership_team, status, role, risk_tier, autonomy_level, allowed_tools, capabilities, governance_tags)
VALUES 
('agent-001', 'tenant-acme', 'prod', 'security', 'active', 'triage', 'medium', 'supervised', ARRAY['siem_query', 'log_search'], ARRAY['alert_triage', 'enrichment'], ARRAY['pci', 'sox']),
('agent-highrisk', 'tenant-acme', 'prod', 'incident-response', 'active', 'containment', 'critical', 'autonomous', ARRAY['containment', 'quarantine', 'block_ip'], ARRAY['host_isolation', 'traffic_blocking'], ARRAY['pci', 'hipaa', 'fedramp']);

-- Test queries
SELECT * FROM agents WHERE agent_id = 'agent-001';
SELECT * FROM agents WHERE agent_id = 'agent-001' AND status = 'active';