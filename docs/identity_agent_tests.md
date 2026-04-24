# Identity Agent Test Documentation




### Detailed Description

| Test ID | Test Name | Test Description | Expected Input | Expected Output |
|---------|----------|-----------------|---------------|----------------|
| T01 | Valid request returns success | Valid request, active agent, valid metadata | `valid_request` payload | `success: true`, `decision_context` populated |
| T02 | Missing agent_id | Missing required field agent_id | `missing_agent_id` payload | `success: false`, error contains "agent_id" |
| T03 | Empty agent_id | Empty string agent_id | `empty_agent_id` payload | `success: false`, error contains "agent_id" |
| T04 | Missing tenant_id | Missing required field tenant_id | `missing_tenant_id` payload | `success: false`, error contains "tenant_id" |
| T05 | Missing environment | Missing required field environment | `missing_environment` payload | `success: false`, error contains "environment" |
| T06 | Whitespace agent_id | Whitespace-only agent_id | `whitespace_agent_id` payload | `success: false`, error contains "agent_id" |
| T07 | Invalid JSON | Malformed JSON payload | "not valid json" string | `success: false`, error contains "invalid" |
| T08 | Unknown agent | Agent not in registry | `unknown_agent` payload | `success: false`, error: "Unknown agent" |
| T09 | Cross-tenant access denied | Wrong tenant_id in request | `cross_tenant` payload | `success: false`, error: "cross-tenant" |
| T10 | Cross-environment access denied | Wrong environment in request | `cross_environment` payload | `success: false`, error: "cross-environment" |
| T11 | Suspended agent denied | Agent status = suspended | `suspended_agent` payload | `success: false`, error contains "suspended" |
| T12 | Disabled agent denied | Agent status = disabled | `disabled_agent` payload | `success: false`, error contains "disabled" |
| T13 | Pending agent denied | Agent status = pending | `pending_agent` payload | `success: false`, error contains "pending" |
| T14 | Missing metadata | Active agent without metadata | `missing_metadata` payload | `success: false`, error: "Missing metadata" |
| T15 | Audit log on success | write_audit_log called | `valid_request` payload | `write_audit_log.called: true`, `decision: ALLOW` |
| T16 | Audit log on denial | write_audit_log called | `suspended_agent` payload | `write_audit_log.called: true`, `decision: DENY` |
| T17 | Audit log required fields | All 11 fields present | `valid_request` payload | All fields non-null |
| T18 | Decision context timestamp | timestamp field present | `valid_request` payload | `timestamp` is not None |
| T19 | Security posture risk_tier | risk_tier passed through | `high_risk_agent` payload | `risk_tier: critical`, `autonomy_level: autonomous` |
| T20 | Security posture allowed_tools | allowed_tools passed through | `high_risk_agent` payload | Tools: containment, quarantine, block_ip |
| T21 | Security posture governance_tags | governance_tags passed through | `high_risk_agent` payload | Tags: pci, hipaa, fedramp |
| T22 | Null db_client | Database not initialized | `valid_request` payload, `db_client=None` | `success: false`, error: "database" |
| T23 | Audit log event_id unique | event_id differs per request | `valid_request` payload (x2) | `event_id1 != event_id2` |
| T24 | Decision context all fields | All 9 fields present | `valid_request` payload | All fields non-null |
| T25 | Response structure correct | Response structure validation | `valid_request` payload | `decision_context`, `audit_event_id`, `error_message` correct |

### Compact Table

| Test ID | Test Name | Expected Input | Expected Output |
|---------|----------|---------------|----------------|
| T01 | Valid request returns success | `valid_request` | `success: true` |
| T02 | Missing agent_id | `missing_agent_id` | `success: false`, error "agent_id" |
| T03 | Empty agent_id | `empty_agent_id` | `success: false`, error "agent_id" |
| T04 | Missing tenant_id | `missing_tenant_id` | `success: false`, error "tenant_id" |
| T05 | Missing environment | `missing_environment` | `success: false`, error "environment" |
| T06 | Whitespace agent_id | `whitespace_agent_id` | `success: false`, error "agent_id" |
| T07 | Invalid JSON | "not valid json" | `success: false`, error "invalid" |
| T08 | Unknown agent | `unknown_agent` | `success: false`, "Unknown agent" |
| T09 | Cross-tenant access denied | `cross_tenant` | `success: false`, "cross-tenant" |
| T10 | Cross-environment access denied | `cross_environment` | `success: false`, "cross-environment" |
| T11 | Suspended agent denied | `suspended_agent` | `success: false`, "suspended" |
| T12 | Disabled agent denied | `disabled_agent` | `success: false`, "disabled" |
| T13 | Pending agent denied | `pending_agent` | `success: false`, "pending" |
| T14 | Missing metadata | `missing_metadata` | `success: false`, "Missing metadata" |
| T15 | Audit log on success | `valid_request` | decision: ALLOW |
| T16 | Audit log on denial | `suspended_agent` | decision: DENY |
| T17 | Audit log required fields | `valid_request` | All 11 fields present |
| T18 | Decision context timestamp | `valid_request` | timestamp non-null |
| T19 | Security posture risk_tier | `high_risk_agent` | risk_tier: critical |
| T20 | Security posture allowed_tools | `high_risk_agent` | Tools match expected |
| T21 | Security posture governance_tags | `high_risk_agent` | Tags match expected |
| T22 | Null db_client | `valid_request`, None | `success: false`, "database" |
| T23 | Audit log event_id unique | `valid_request` (x2) | event_ids differ |
| T24 | Decision context all fields | `valid_request` | All 9 fields present |
| T25 | Response structure correct | `valid_request` | Structure correct |

---

## Test Coverage by Flow Step

The Identity Agent flow has 7 steps. Each step is tested comprehensively.

### Step 1: Validate Request

Tests validation of incoming request payloads.

| Test ID | Test Name | Scenario |
|--------|----------|---------|
| T02 | Missing agent_id | Required field missing |
| T03 | Empty agent_id | Empty string |
| T04 | Missing tenant_id | Required field missing |
| T05 | Missing environment | Required field missing |
| T06 | Whitespace agent_id | Whitespace-only value |
| T07 | Invalid JSON | Malformed JSON payload |

### Step 2: Registry Lookup

Tests agent lookup in registry tables.

| Test ID | Test Name | Scenario |
|--------|----------|---------|
| T08 | Unknown agent | Agent not in any registry table |
| T09 | Cross-tenant | Wrong tenant_id in request |
| T10 | Cross-environment | Wrong environment in request |

### Step 3: Status Decision

Tests active/blocked decision handling.

| Test ID | Test Name | Status |
|--------|----------|-------|
| T11 | Suspended | suspended |
| T12 | Disabled | disabled |
| T13 | Pending | pending |

### Step 4: Fetch Metadata

Tests metadata retrieval for active agents.

| Test ID | Test Name | Scenario |
|--------|----------|---------|
| T14 | Missing metadata | Active agent without metadata |

### Step 5: Build Decision Context

Tests output contract construction.

| Test ID | Test Name | Verification |
|--------|----------|-------------|
| T18 | Decision context timestamp | timestamp field present |
| T24 | All required fields | All 9 fields present |

### Step 6: Audit Log

Tests tamper-evident audit logging.

| Test ID | Test Name | Scenario |
|--------|----------|---------|
| T15 | Audit log on success | write_audit_log called |
| T16 | Audit log on denial | write_audit_log called |
| T17 | Required fields | All 11 fields present |
| T23 | Unique event_id | event_id differs per request |

### Step 7: Return Output

Tests final response structure.

| Test ID | Test Name | Scenario |
|--------|----------|---------|
| T01 | Valid request | Full success flow |
| T22 | Null db_client | Database not initialized |
| T25 | Response structure | All response fields |

---
