# Identity Agent Test Specification

---

## Test T01: Valid Request - Success

| Field | Value |
|-------|-------|
| **Test ID** | T01 |
| **Description** | Valid request, active agent, valid metadata |
| **Input** | agent_id: agent-001, tenant_id: tenant-acme, environment: prod, session_id: sess-12345, origin: 192.168.1.100, network_zone: dmz |
| **Mock Setup** | Registry: agent-001 (active), Metadata: agent-001 exists |
| **If ACCEPTED** | success: true, decision_context populated with agent_id, status: "active" |
| **If REJECTED** | Test fails - invalid request got rejected |

---

## Test T02: Missing Agent ID

| Field | Value |
|-------|-------|
| **Test ID** | T02 |
| **Description** | Missing agent_id in request |
| **Input** | tenant_id: tenant-acme, environment: prod (no agent_id) |
| **Mock Setup** | Registry: agent-001 (active), Metadata: agent-001 exists |
| **If ACCEPTED** | Test fails - request should be rejected for missing agent_id |
| **If REJECTED** | success: false, error_message contains "agent_id" |

---

## Test T03: Empty Agent ID

| Field | Value |
|-------|-------|
| **Test ID** | T03 |
| **Description** | Empty agent_id string |
| **Input** | agent_id: "", tenant_id: tenant-acme, environment: prod |
| **Mock Setup** | Registry: agent-001 (active), Metadata: agent-001 exists |
| **If ACCEPTED** | Test fails - empty agent_id should be rejected |
| **If REJECTED** | success: false, error_message contains "agent_id" |

---

## Test T04: Missing Tenant ID

| Field | Value |
|-------|-------|
| **Test ID** | T04 |
| **Description** | Missing tenant_id in request |
| **Input** | agent_id: agent-001, environment: prod (no tenant_id) |
| **Mock Setup** | Registry: agent-001 (active), Metadata: agent-001 exists |
| **If ACCEPTED** | Test fails - request should be rejected for missing tenant_id |
| **If REJECTED** | success: false, error_message contains "tenant_id" |

---

## Test T05: Missing Environment

| Field | Value |
|-------|-------|
| **Test ID** | T05 |
| **Description** | Missing environment in request |
| **Input** | agent_id: agent-001, tenant_id: tenant-acme (no environment) |
| **Mock Setup** | Registry: agent-001 (active), Metadata: agent-001 exists |
| **If ACCEPTED** | Test fails - request should be rejected for missing environment |
| **If REJECTED** | success: false, error_message contains "environment" |

---

## Test T06: Whitespace Agent ID

| Field | Value |
|-------|-------|
| **Test ID** | T06 |
| **Description** | Whitespace-only agent_id |
| **Input** | agent_id: "   ", tenant_id: tenant-acme, environment: prod |
| **Mock Setup** | Registry: agent-001 (active), Metadata: agent-001 exists |
| **If ACCEPTED** | Test fails - whitespace agent_id should be rejected |
| **If REJECTED** | success: false, error_message contains "agent_id" |

---

## Test T07: Invalid JSON Payload

| Field | Value |
|-------|-------|
| **Test ID** | T07 |
| **Description** | Invalid JSON payload |
| **Input** | "not valid json" (string, not JSON) |
| **Mock Setup** | Registry: agent-001 (active), Metadata: agent-001 exists |
| **If ACCEPTED** | Test fails - invalid JSON should be rejected |
| **If REJECTED** | success: false, error_message contains "invalid" |

---

## Test T08: Unknown Agent

| Field | Value |
|-------|-------|
| **Test ID** | T08 |
| **Description** | Agent not in registry |
| **Input** | agent_id: agent-unknown, tenant_id: tenant-acme, environment: prod |
| **Mock Setup** | No registry records for agent-unknown |
| **If ACCEPTED** | Test fails - unknown agent should be rejected |
| **If REJECTED** | success: false, error_message: "unknown agent" |

---

## Test T09: Cross-Tenant Access

| Field | Value |
|-------|-------|
| **Test ID** | T09 |
| **Description** | Agent belongs to different tenant |
| **Input** | agent_id: agent-001, tenant_id: wrong-tenant, environment: prod |
| **Mock Setup** | Registry: agent-001 belongs to tenant-acme (not wrong-tenant) |
| **If ACCEPTED** | Test fails - cross-tenant access should be rejected |
| **If REJECTED** | success: false, error_message: "cross-tenant" |

---

## Test T10: Cross-Environment Access

| Field | Value |
|-------|-------|
| **Test ID** | T10 |
| **Description** | Agent belongs to different environment |
| **Input** | agent_id: agent-001, tenant_id: tenant-acme, environment: staging |
| **Mock Setup** | Registry: agent-001 belongs to prod (not staging) |
| **If ACCEPTED** | Test fails - cross-environment access should be rejected |
| **If REJECTED** | success: false, error_message: "cross-environment" |

---

## Test T11: Suspended Agent

| Field | Value |
|-------|-------|
| **Test ID** | T11 |
| **Description** | Agent status = suspended |
| **Input** | agent_id: agent-001, tenant_id: tenant-acme, environment: prod |
| **Mock Setup** | Registry: agent-001 status: suspended |
| **If ACCEPTED** | Test fails - suspended agent should be rejected |
| **If REJECTED** | success: false, error_message contains "suspended" |

---

## Test T12: Disabled Agent

| Field | Value |
|-------|-------|
| **Test ID** | T12 |
| **Description** | Agent status = disabled |
| **Input** | agent_id: agent-001, tenant_id: tenant-acme, environment: prod |
| **Mock Setup** | Registry: agent-001 status: disabled |
| **If ACCEPTED** | Test fails - disabled agent should be rejected |
| **If REJECTED** | success: false, error_message contains "disabled" |

---

## Test T13: Pending Agent

| Field | Value |
|-------|-------|
| **Test ID** | T13 |
| **Description** | Agent status = pending |
| **Input** | agent_id: agent-001, tenant_id: tenant-acme, environment: prod |
| **Mock Setup** | Registry: agent-001 status: pending |
| **If ACCEPTED** | Test fails - pending agent should be rejected |
| **If REJECTED** | success: false, error_message contains "pending" |

---

## Test T14: Missing Metadata

| Field | Value |
|-------|-------|
| **Test ID** | T14 |
| **Description** | Active agent but no metadata record |
| **Input** | agent_id: agent-001, tenant_id: tenant-acme, environment: prod |
| **Mock Setup** | Registry: agent-001 active, NO metadata |
| **If ACCEPTED** | Test fails - missing metadata should cause rejection |
| **If REJECTED** | success: false, error_message: "missing metadata" |

---

## Test T15: Audit Log on Denial

| Field | Value |
|-------|-------|
| **Test ID** | T15 |
| **Description** | Audit log written on denied request |
| **Input** | Same as T11 (suspended agent) |
| **Mock Setup** | Registry: agent-001 suspended |
| **If ACCEPTED** | Test fails - denied request should have DENY decision |
| **If REJECTED** | write_audit_log called, decision: "DENY" |

---

## Test T16: Audit Log Required Fields

| Field | Value |
|-------|-------|
| **Test ID** | T16 |
| **Description** | Audit log has all required fields |
| **Input** | Same as T01 (valid request) |
| **Mock Setup** | Registry: agent-001 active, Metadata: exists |
| **If ACCEPTED** | All fields present in audit log |
| **If REJECTED** | Test fails - missing fields in audit log |

**Required Fields**: event_id, timestamp, agent_id, session_id, tenant_id, environment, origin, network_zone, event_type, decision, reason

---

## Test T17: Decision Context Timestamp

| Field | Value |
|-------|-------|
| **Test ID** | T17 |
| **Description** | Decision context has timestamp |
| **Input** | Same as T01 (valid request) |
| **Mock Setup** | Registry: agent-001 active, Metadata: exists |
| **If ACCEPTED** | decision_context.timestamp is not None |
| **If REJECTED** | Test fails - timestamp should still be populated |

---

## Test T18: Security Posture - Risk Tier

| Field | Value |
|-------|-------|
| **Test ID** | T18 |
| **Description** | Risk tier passed through in metadata |
| **Input** | agent_id: agent-highrisk, tenant_id: tenant-acme, environment: prod |
| **Mock Setup** | Registry: agent-highrisk active, Metadata: risk_tier: critical, autonomy_level: autonomous |
| **If ACCEPTED** | decision_context.metadata.risk_tier == "critical", autonomy_level == "autonomous" |
| **If REJECTED** | Test fails - metadata should be passed through |

---

## Test T19: Security Posture - Allowed Tools

| Field | Value |
|-------|-------|
| **Test ID** | T19 |
| **Description** | Allowed tools passed through in metadata |
| **Input** | agent_id: agent-highrisk, tenant_id: tenant-acme, environment: prod |
| **Mock Setup** | Registry: agent-highrisk active, Metadata: allowed_tools: [containment, quarantine, block_ip] |
| **If ACCEPTED** | decision_context.metadata.allowed_tools == [containment, quarantine, block_ip] |
| **If REJECTED** | Test fails - allowed_tools should be passed through |

---

## Test T20: Security Posture - Governance Tags

| Field | Value |
|-------|-------|
| **Test ID** | T20 |
| **Description** | Governance tags passed through in metadata |
| **Input** | agent_id: agent-highrisk, tenant_id: tenant-acme, environment: prod |
| **Mock Setup** | Registry: agent-highrisk active, Metadata: governance_tags: [pci, hipaa, fedramp] |
| **If ACCEPTED** | decision_context.metadata.governance_tags == [pci, hipaa, fedramp] |
| **If REJECTED** | Test fails - governance_tags should be passed through |

---

## Test T21: Null Database Client

| Field | Value |
|-------|-------|
| **Test ID** | T21 |
| **Description** | Null database client returns error |
| **Input** | Same as T01 (valid request) |
| **Mock Setup** | db_client = None |
| **If ACCEPTED** | Test fails - null db_client should cause rejection |
| **If REJECTED** | success: false, error_message contains "database" |

---

## Test T22: Audit Log Event ID Unique

| Field | Value |
|-------|-------|
| **Test ID** | T22 |
| **Description** | Event IDs are unique per request |
| **Input** | Same as T01 (valid request) |
| **Mock Setup** | Registry: agent-001 active, Metadata: exists |
| **If ACCEPTED (Unique)** | result1.audit_event_id != result2.audit_event_id |
| **If REJECTED (Duplicate)** | Test fails - event IDs should be unique |

---

## Test T23: Decision Context All Fields

| Field | Value |
|-------|-------|
| **Test ID** | T23 |
| **Description** | Decision context has all required fields |
| **Input** | Same as T01 (valid request) |
| **Mock Setup** | Registry: agent-001 active, Metadata: exists |
| **If ACCEPTED** | All fields present: agent_id, tenant_id, environment, network_zone, origin, session_id, metadata, status, timestamp |
| **If REJECTED** | Test fails - missing fields in decision context |

---

## Test T24: Response Structure

| Field | Value |
|-------|-------|
| **Test ID** | T24 |
| **Description** | FinalResponse has correct structure |
| **Input** | Same as T01 (valid request) |
| **Mock Setup** | Registry: agent-001 active, Metadata: exists |
| **If ACCEPTED** | decision_context != None, audit_event_id != None, error_message == None |
| **If REJECTED** | decision_context == None, error_message != None, audit_event_id != None |

---

## Summary Table

| Test ID | Test Name | Expected | If Not |
|--------|----------|----------|--------|
| T01 | Valid Request Success | ACCEPTED | REJECTED (invalid request accepted) |
| T02 | Missing Agent ID | REJECTED | ACCEPTED (should reject) |
| T03 | Empty Agent ID | REJECTED | ACCEPTED (should reject) |
| T04 | Missing Tenant ID | REJECTED | ACCEPTED (should reject) |
| T05 | Missing Environment | REJECTED | ACCEPTED (should reject) |
| T06 | Whitespace Agent ID | REJECTED | ACCEPTED (should reject) |
| T07 | Invalid JSON | REJECTED | ACCEPTED (should reject) |
| T08 | Unknown Agent | REJECTED | ACCEPTED (should reject) |
| T09 | Cross-Tenant Access | REJECTED | ACCEPTED (security issue) |
| T10 | Cross-Environment Access | REJECTED | ACCEPTED (security issue) |
| T11 | Suspended Agent | REJECTED | ACCEPTED (should reject) |
| T12 | Disabled Agent | REJECTED | ACCEPTED (should reject) |
| T13 | Pending Agent | REJECTED | ACCEPTED (should reject) |
| T14 | Missing Metadata | REJECTED | ACCEPTED (should reject) |
| T15 | Audit Log on Denial | REJECTED + Audit | No audit written |
| T16 | Audit Log Fields | All fields | Missing fields |
| T17 | Decision Timestamp | Present | Missing |
| T18 | Risk Tier Pass-through | Present | Missing |
| T19 | Allowed Tools Pass-through | Present | Missing |
| T20 | Governance Tags Pass-through | Present | Missing |
| T21 | Null DB Client | REJECTED | ACCEPTED (should reject) |
| T22 | Unique Event IDs | Unique | Duplicate |
| T23 | Decision Context Fields | All fields | Missing fields |
| T24 | Response Structure | Correct | Incorrect structure |