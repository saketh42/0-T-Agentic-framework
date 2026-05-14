-- Identity Agent - Windows Database Setup
-- Run: psql -U postgres -f setup_windows.sql

CREATE DATABASE identity_agent;
\c identity_agent

CREATE TABLE agents (
    agent_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    environment TEXT NOT NULL,
    ownership_team TEXT,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT,
    role TEXT,
    risk_tier TEXT,
    autonomy_level TEXT,
    allowed_tools TEXT[],
    capabilities TEXT[],
    governance_tags TEXT[]
);

CREATE INDEX idx_agents_tenant ON agents(tenant_id);
CREATE INDEX idx_agents_status ON agents(status);

INSERT INTO agents (agent_id, tenant_id, environment, ownership_team, status, role, risk_tier, autonomy_level, allowed_tools, capabilities, governance_tags)
VALUES
('agent-001', 'tenant-acme', 'prod', 'security', 'active', 'triage', 'medium', 'supervised', ARRAY['siem_query', 'log_search'], ARRAY['alert_triage', 'enrichment'], ARRAY['pci', 'sox']),
('agent-002', 'tenant-acme', 'prod', 'security', 'suspended', 'triage', 'medium', 'supervised', ARRAY['siem_query'], ARRAY['alert_triage'], ARRAY['pci']),
('agent-003', 'tenant-acme', 'prod', 'security', 'disabled', 'triage', 'low', 'supervised', ARRAY['log_search'], ARRAY['enrichment'], ARRAY['sox']),
('agent-004', 'tenant-acme', 'prod', 'devops', 'pending', 'monitor', 'high', 'autonomous', ARRAY['deploy'], ARRAY['automation'], ARRAY['fedramp']),
('agent-highrisk', 'tenant-acme', 'prod', 'incident-response', 'active', 'containment', 'critical', 'autonomous', ARRAY['containment', 'quarantine', 'block_ip'], ARRAY['host_isolation', 'traffic_blocking'], ARRAY['pci', 'hipaa', 'fedramp']);
