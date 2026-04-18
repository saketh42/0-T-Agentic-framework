# Identity Agent Test Documentation

## Overview

This document details the test strategy, test data, and coverage for the Identity Agent component of the Agentic Security Platform. The tests follow a **test-first approach** with comprehensive coverage of all 7 steps in the identity validation flow.

---

## 1. Test Architecture

### 1.1 Directory Structure

```
tests/
├── test_identity_runner.py      # Main test runner (27 tests)
├── test_data/
│   ├── identity_agent_inputs.json   # Test request payloads
│   └── identity_agent_mocks.json  # Mock data for DB
└── debug_test.py
```

### 1.2 Running Tests

```bash
python3 tests/test_identity_runner.py
```

Output:
```
==================================================
Identity Agent Test Suite
==================================================
Loaded 14 test requests from JSON
Loaded 2 registry records from JSON
Loaded 2 metadata records from JSON


==================================================
RESULTS: 27 passed, 0 failed
==================================================
```

---

## 2. Test Data Files

### 2.1 identity_agent_inputs.json

Contains 14 test request payloads covering various scenarios:

| Key | Description |
|-----|------------|
| `valid_request` | Complete valid request |
| `missing_agent_id` | Missing required field |
| `empty_agent_id` | Empty string value |
| `missing_tenant_id` | Missing tenant_id |
| `missing_environment` | Missing environment |
| `whitespace_agent_id` | Whitespace-only value |
| `unknown_agent` | Agent not in registry |
| `cross_tenant` | Wrong tenant access attempt |
| `cross_environment` | Wrong environment access attempt |
| `suspended_agent` | Suspended status agent |
| `disabled_agent` | Disabled status agent |
| `pending_agent` | Pending status agent |
| `missing_metadata` | Active agent without metadata |
| `high_risk_agent` | High/critical risk agent |

**Schema:**
```json
{
  "requests": {
    "<key>": {
      "agent_id": "string",
      "tenant_id": "string",
      "environment": "string",
      "session_id": "string",
      "origin": "string",
      "network_zone": "string"
    }
  }
}
```

### 2.2 identity_agent_mocks.json

Contains mock database data for testing:

#### Registry Records

| Agent | Status | Tenant | Environment | Risk Tier |
|-------|--------|--------|--------------|-----------|
| agent-001 | active | tenant-acme | prod | medium |
| agent-001 | suspended | tenant-acme | prod | - |
| agent-001 | disabled | tenant-acme | prod | - |
| agent-001 | pending | tenant-acme | prod | - |
| agent-highrisk | active | tenant-acme | prod | critical |

#### Metadata Records

**agent-001:**
- role: "triage"
- risk_tier: "medium"
- autonomy_level: "supervised"
- allowed_tools: ["siem_query", "log_search"]
- capabilities: ["alert_triage", "enrichment"]
- governance_tags: ["pci", "sox"]

**agent-highrisk:**
- role: "containment"
- risk_tier: "critical"
- autonomy_level: "autonomous"
- allowed_tools: ["containment", "quarantine", "block_ip"]
- capabilities: ["host_isolation", "traffic_blocking"]
- governance_tags: ["pci", "hipaa", "fedramp"]

---

## 3. Test Coverage by Flow Step

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

**Expected Behavior:**
- Return `success: false`
- Error message contains field name

### Step 2: Registry Lookup

Tests agent lookup in registry tables.

| Test ID | Test Name | Scenario |
|--------|----------|---------|
| T08 | Unknown agent | Agent not in any registry table |
| T09 | Cross-tenant | Wrong tenant_id in request |
| T10 | Cross-environment | Wrong environment in request |

**Expected Behavior:**
- T08: Return "Unknown agent" error
- T09: Return "Cross-tenant access attempt detected"
- T10: Return "Cross-environment access attempt detected"

### Step 3: Status Decision

Tests active/blocked decision handling.

| Test ID | Test Name | Status |
|--------|----------|-------|
| T11 | Suspended | suspended |
| T12 | Disabled | disabled |
| T13 | Pending | pending |

**Expected Behavior:**
- Return `success: false`
- Error message includes current status
- Deny access

### Step 4: Fetch Metadata

Tests metadata retrieval for active agents.

| Test ID | Test Name | Scenario |
|--------|----------|---------|
| T14 | Missing metadata | Active agent without metadata |

**Expected Behavior:**
- Return "Missing metadata in DB" error
- success: false

### Step 5: Build Decision Context

Tests output contract construction.

| Test ID | Test Name | Verification |
|--------|----------|-------------|
| T18 | Decision context timestamp | timestamp field present |
| T24 | All required fields | All 9 fields present |

**Required Fields in IdentityDecisionContext:**
1. agent_id
2. tenant_id
3. environment
4. network_zone
5. origin
6. session_id
7. metadata (AgentMetadata)
8. status
9. timestamp

### Step 6: Audit Log

Tests tamper-evident audit logging.

| Test ID | Test Name | Scenario |
|--------|----------|---------|
| T15 | Audit log on success | write_audit_log called |
| T15b | Audit decision ALLOW | decision == "ALLOW" |
| T16 | Audit log on denial | write_audit_log called |
| T16b | Audit decision DENY | decision == "DENY" |
| T17 | Required fields | All 11 fields present |
| T23 | Unique event_id | event_id differs per request |

**Required Fields in AuditLogEvent:**
1. event_id
2. timestamp
3. agent_id
4. session_id
5. tenant_id
6. environment
7. origin
8. network_zone
9. event_type
10. decision
11. reason

### Step 7: Return Output

Tests final response structure.

| Test ID | Test Name | Scenario |
|--------|----------|---------|
| T01 | Valid request | Full success flow |
| T19 | Null db_client | Database not initialized |
| T25 | Response structure | All response fields |

---

## 4. Security Posture Tests

Tests verify security posture attributes are passed through correctly.

### T19: risk_tier

Verifies risk_tier from metadata is passed to decision context.

```python
passed = (result.decision_context.metadata.risk_tier == "critical" and
          result.decision_context.metadata.autonomy_level == "autonomous")
```

### T20: allowed_tools

Verifies allowed_tools list is passed through.

```python
expected_tools = ["containment", "quarantine", "block_ip"]
actual_tools = result.decision_context.metadata.allowed_tools
```

### T21: governance_tags

Verifies governance compliance tags are passed through.

```python
expected_tags = ["pci", "hipaa", "fedramp"]
actual_tags = result.decision_context.metadata.governance_tags
```

---

## 5. Test Implementation Details

### 5.1 Mock Database Client

The test uses a mock `DatabaseClient` that simulates the database interface:

```python
class DatabaseClient:
    def fetch_from_registry_active(self, agent_id: str) -> Optional[RegistryRecord]
    def fetch_from_registry_suspended(self, agent_id: str) -> Optional[RegistryRecord]
    def fetch_from_registry_disabled(self, agent_id: str) -> Optional[RegistryRecord]
    def fetch_from_registry_pending(self, agent_id: str) -> Optional[RegistryRecord]
    def fetch_agent_metadata(self, agent_id: str) -> Optional[AgentMetadata]
    def write_audit_log(self, log_event: AuditLogEvent) -> bool
```

### 5.2 Helper Functions

**create_mock_db_client_for_status()**
Creates a mock DB client configured for a specific agent status:

```python
def create_mock_db_client_for_status(agent_id, status, has_metadata=True):
    #Configure registry table based on status
    #Configure metadata if has_metadata=True
```

**create_registry_record()**
Creates RegistryRecord from mock JSON data.

**create_metadata()**
Creates AgentMetadata from mock JSON data.

### 5.3 Test Results Tracker

Simple results tracking:

```python
class TestResults:
    def add(self, test_name, passed, message="")
    def summary(self) -> str
```

---

## 6. Adding New Tests

### 6.1 Add Test Data to JSON

1. Add new request to `identity_agent_inputs.json`:

```json
"new_scenario": {
  "agent_id": "agent-002",
  "tenant_id": "tenant-acme",
  "environment": "prod",
  "session_id": "sess-99999",
  "origin": "192.168.1.200",
  "network_zone": "internal"
}
```

2. Add mock data to `identity_agent_mocks.json` if needed.

### 6.2 Add Test Function

```python
def test_tXX_description(results):
    """TXX: Test description"""
    payload = TEST_INPUTS["requests"]["new_scenario"]
    mock_db = create_mock_db_client_for_status("agent-002", "active")
    result = identity_agent_flow(payload, mock_db)
    
    passed = result.success is True  # Add assertion
    results.add("TXX: Description", passed, result.error_message if not passed else "")
```

### 6.3 Register Test in main()

```python
def main():
    # ... existing tests ...
    test_tXX_description(results)
```

---

## 7. Test Execution Matrix

| Status | Active | Suspended | Disabled | Pending | Unknown |
|--------|--------|----------|-----------|---------|---------|
| Valid request | T01 | - | - | - | - |
| Missing fields | T02-T06 | T02-T06 | T02-T06 | T02-T06 | - |
| Cross-tenant | T09 | T09 | T09 | T09 | - |
| Cross-env | T10 | T10 | T10 | T10 | - |
| No metadata | T14 | - | - | - | - |
| Null DB | T19 | T19 | T19 | T19 | T19 |

---

## 8. Success Criteria

All tests must pass for the Identity Agent to be considered production-ready:

- [x] All 27 tests passing
- [x] Test data externalized to JSON
- [x] Full coverage of 7 flow steps
- [x] Security posture verification
- [x] Audit log completeness
- [x] Response structure validation

---

## 9. Future Enhancements

Potential additions:

1. **pytest integration** - Convert to pytest framework
2. **Parameterized tests** - Use pytest.mark.parametrize
3. **Property-based tests** - Use hypothesis for random inputs
4. **Performance tests** - Response time benchmarks
5. **Integration tests** - Connect to actual database
6. **Contract tests** - Verify schema compatibility

---

## 10. Reference

- **Main Documentation**: `docs/main.md`
- **Persona Documentation**: `docs/personas.md`
- **Pseudocode**: `pseudocode/identity_agent.py`
- **Database Schema**: `db_schema.sql`