# Identity Agent Test Documentation

## Test Cases

| Test ID | Test Name | Input | Expected Output |
|---------|-----------|-------|-----------------|
| T01 | Valid request returns success | `valid_request` | `authorization: ALLOW`, `identity_context` populated |
| T02 | Missing agent_id | `missing_agent_id` | `authorization: DENY`, `failure_reason` contains "agent_id" |
| T03 | Empty agent_id | `empty_agent_id` | `authorization: DENY`, `failure_reason` contains "agent_id" |
| T04 | Missing tenant_id | `missing_tenant_id` | `authorization: DENY`, `failure_reason` contains "tenant_id" |
| T05 | Missing environment | `missing_environment` | `authorization: DENY`, `failure_reason` contains "environment" |
| T06 | Whitespace agent_id | `whitespace_agent_id` | `authorization: DENY`, `failure_reason` contains "agent_id" |
| T07 | Invalid JSON payload | `"not valid json"` | `authorization: DENY`, `failure_reason` contains "invalid" |
| T08 | Unknown agent | `unknown_agent` | `authorization: BLOCK`, `failure_reason` contains "unknown agent" |
| T09 | Cross-tenant access | `cross_tenant` | `authorization: DENY`, `failure_reason` contains "cross-tenant" |
| T10 | Cross-environment access | `cross_environment` | `authorization: DENY`, `failure_reason` contains "cross-environment" |
| T11 | Suspended agent | `suspended_agent` | `authorization: DENY`, `failure_reason` contains "suspended" |
| T12 | Disabled agent | `disabled_agent` | `authorization: DENY`, `failure_reason` contains "disabled" |
| T13 | Pending agent | `pending_agent` | `authorization: DENY`, `failure_reason` contains "pending" |
| T14 | Missing metadata | `missing_metadata` | `authorization: DENY`, `failure_reason` contains "missing metadata" |
| T18 | Decision context timestamp | `valid_request` | `identity_context.timestamp` is not None |
| T19 | Risk tier pass-through | `high_risk_agent` | `identity_context.metadata.risk_tier == "critical"` |
| T20 | Allowed tools pass-through | `high_risk_agent` | Tools match expected list |
| T21 | Governance tags pass-through | `high_risk_agent` | Tags match expected list |
| T22 | Null db_client | `valid_request`, `db_client=None` | `authorization: DENY`, `failure_reason` contains "database" |
| T24 | Decision context all fields | `valid_request` | All 9 fields non-null |
| T25 | Response structure correct | `valid_request` | `identity_context` non-null, `failure_reason` null |

---

## Test Coverage by Flow Step

### Step 1: Validate Request

| Test ID | Scenario |
|---------|----------|
| T02 | Missing agent_id |
| T03 | Empty agent_id |
| T04 | Missing tenant_id |
| T05 | Missing environment |
| T06 | Whitespace agent_id |
| T07 | Invalid JSON payload |

### Step 2: Registry Lookup

| Test ID | Scenario |
|---------|----------|
| T08 | Agent not in any registry table |
| T09 | Wrong tenant_id in request |
| T10 | Wrong environment in request |

### Step 3: Status Decision

| Test ID | Status |
|---------|--------|
| T11 | suspended |
| T12 | disabled |
| T13 | pending |

### Step 4: Fetch Metadata

| Test ID | Scenario |
|---------|----------|
| T14 | Active agent without metadata |

### Step 5: Build Decision Context

| Test ID | Verification |
|---------|-------------|
| T18 | timestamp field present |
| T24 | All 9 required fields present |

### Step 6: Submit to Gateway

| Test ID | Verification |
|---------|-------------|
| T01 | Full success flow (ALLOW + JWT + STM storage) |
| T19 | Risk tier passed through |
| T20 | Allowed tools passed through |
| T21 | Governance tags passed through |

### Error Handling

| Test ID | Scenario |
|---------|----------|
| T22 | Database not initialized |
| T25 | Response structure validation |

---

## JWT Tests

JWT tests verify the `issue_agent_jwt()` function.

| Test | Description |
|------|-------------|
| JWT issuance | Token issued and is non-empty string |
| JWT decode | Decodes with corresponding public key |
| JWT standard claims | Contains `sub`, `iss`, `iat`, `exp` |
| JWT expiration | `exp` is in the future |
| Different agents | Different `sub` claim per agent |
| Invalid signature | Wrong public key rejects the token |
| Env var loading | Key loaded from `IDENTITY_PRIVATE_KEY` env var |
| Missing key | Raises `RuntimeError` when no key available |

---

## STM Tests

STM tests cover both mock and Redis-backed implementations.

| Test Count | Scope |
|-----------|-------|
| 16 | Mock STM interface tests |
| 3 | Redis integration tests (skipped if Redis unavailable) |
