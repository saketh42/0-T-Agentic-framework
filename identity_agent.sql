-- Identity Agent Database Schema
-- Single table for agents

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE agents (
    agent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    purpose TEXT,
    role VARCHAR(50),
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    risk_tier VARCHAR(32),
    autonomy_level VARCHAR(32),
    ownership_team VARCHAR(100),
    governance_tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agents_tenant ON agents(tenant_id);
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_role_risk ON agents(role, risk_tier);

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
INSERT INTO agents (agent_id, tenant_id, name, type, purpose, role, status, risk_tier, autonomy_level, ownership_team, governance_tags)
VALUES 
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'tenant-acme', 'Triage Agent', 'triage', 'Alert triage and enrichment', 'triage', 'active', 'medium', 'propose', 'security', ARRAY['pci', 'sox']),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'tenant-acme', 'Containment Agent', 'containment', 'Incident containment and isolation', 'containment', 'active', 'critical', 'execute', 'incident-response', ARRAY['pci', 'hipaa', 'fedramp']),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'tenant-acme', 'Suspended Agent', 'triage', 'Test suspended', 'triage', 'suspended', 'low', 'read_only', 'security', ARRAY[]::TEXT[]);

-- Test queries
SELECT * FROM agents WHERE agent_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';
SELECT * FROM agents WHERE agent_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' AND status = 'active';