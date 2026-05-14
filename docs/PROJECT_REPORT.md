# Identity Module - Project Report

## 1. Scope

The Identity Module validates agent identity, issues JWTs, and builds decision context before Gateway evaluation.

### In Scope

| Area | Description |
|------|-------------|
| Identity validation | Validates agent registration, tenant, and environment |
| Registry lookup | Checks active, suspended, disabled, and pending agent statuses |
| Metadata enrichment | Fetches role, risk tier, autonomy level, and allowed tools |
| Decision context building | Packages all agent attributes into a structured context |
| JWT issuance | Signs RS256 JWT with agent identity claims |
| Gateway submission | Sends validated context to Gateway for policy evaluation |
| STM integration | Redis-backed per-session agent memory |
| Fail-closed behavior | Deny by default when agent is unknown or inactive |

### Out of Scope

| Area | Handled By |
|------|------------|
| Audit logging | Gateway Audit Logchain (docs/main.md §6.4) |
| Policy evaluation | Gateway |
| DLP / Privacy | Privacy/DLP Agent |

---

## 2. Current Status

All Phase 1 implementation is complete.

### Completed

| Work Item | Status |
|-----------|--------|
| Pydantic request/response models | Completed |
| Validation logic (request + required fields) | Completed |
| Database connection layer | Completed |
| Registry lookup (4 status tables) | Completed |
| Metadata fetching | Completed |
| Decision context builder | Completed |
| Gateway submission | Completed |
| JWT issuance (RS256, DB key storage, JWKS endpoint) | Completed |
| STM abstract interface | Completed |
| STM Redis client | Completed |
| FastAPI server (validate, JWKS, STM endpoints) | Completed |
| Key generation CLI | Completed |
| Unit test files | Completed |
| JWT tests | Completed |
| STM tests | Completed |
| Schema evolution | Completed |
| Code review | Completed |

### Pending

| Work Item | Status |
|-----------|--------|
| Gateway integration validation (end-to-end) | Pending |
| Final sign-off | Not started |

---

## 3. Architecture

```
Client / Agent
  |
  v
Identity & Context Service (identity_agent_service)
  |
  +--> Validation Layer (validate_identity_validation_request, validate_required_request_fields)
  |
  +--> Database Layer (establish_identity_agent_db_connection, lookup_agent_in_identity_registry, fetch_agent_security_metadata)
  |
  +--> Decision Context Builder (build_identity_decision_context)
  |
  +--> JWT Issuance (issue_agent_jwt)
  |
  +--> Gateway Submission (submit_decision_context_to_gateway)
  |
  +--> STM Layer (create_session, store_decision_context)
  |
  v
Gateway
```

### File Structure

| File | Purpose |
|------|---------|
| `src/identity_agent.py` | Main orchestrator |
| `src/validate_request.py` | Request validation |
| `src/connect_db.py` | Database connection |
| `src/check_registry.py` | Registry lookup |
| `src/fetch_metadata.py` | Metadata fetching |
| `src/build_decision_context.py` | Decision context builder |
| `src/send_to_policy_agent.py` | Gateway submission |
| `src/issue_jwt.py` | JWT signing and JWK conversion |
| `src/generate_key.py` | RSA key generation CLI |
| `src/schemas.py` | Pydantic models |
| `src/database.py` | Database abstract interface |
| `src/postgres_client.py` | PostgreSQL implementation |
| `src/stm.py` | STM abstract interface |
| `src/stm_redis_client.py` | Redis STM implementation |
| `src/api.py` | FastAPI server |

---

## 4. Execution Flow

1. Agent sends identity request to Identity Service
2. Request parsed into `IdentityValidationRequest` (Pydantic validation)
3. Required fields checked (agent_id, tenant_id, environment)
4. Database connection established
5. Agent looked up in registry across all status tables
6. Cross-tenant access validated
7. Agent status checked (only active allowed)
8. Agent metadata fetched (role, risk, tools, etc.)
9. Decision context built with timestamp
10. JWT issued (RS256, signed with active key from `signing_keys` table)
11. Decision context stored in Redis STM (1-hour TTL)
12. Context submitted to Gateway
13. Final response returned:
    - Success: `authorization: ALLOW`, `identity_context` with JWT token
    - Failure: `authorization: DENY/BLOCK`, `failure_reason`

---

## 5. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/validate` | Agent identity validation, returns ALLOW/DENY/BLOCK with JWT |
| `GET` | `/.well-known/jwks.json?kid=` | Public signing keys for JWT verification |
| `GET` | `/stm` | View current STM sessions |

---

## 6. Test Files

| Test File | Purpose | Status |
|-----------|---------|--------|
| `tests/input_validation/test_t01_valid_request.py` | Valid request handling | Finalized |
| `tests/input_validation/test_t02_missing_agent_id.py` | Missing agent_id | Finalized |
| `tests/input_validation/test_t03_empty_agent_id.py` | Empty agent_id | Finalized |
| `tests/input_validation/test_t04_missing_tenant_id.py` | Missing tenant_id | Finalized |
| `tests/input_validation/test_t05_missing_environment.py` | Missing environment | Finalized |
| `tests/input_validation/test_t06_whitespace_agent_id.py` | Whitespace agent_id | Finalized |
| `tests/registry_lookup/test_t08_unknown_agent.py` | Unknown agent | Finalized |
| `tests/registry_lookup/test_t09_cross_tenant.py` | Cross-tenant detection | Finalized |
| `tests/registry_lookup/test_t10_cross_environment.py` | Cross-environment | Finalized |
| `tests/status_decision/test_t11_suspended.py` | Suspended agent | Finalized |
| `tests/status_decision/test_t12_disabled.py` | Disabled agent | Finalized |
| `tests/status_decision/test_t13_pending.py` | Pending agent | Finalized |
| `tests/metadata/test_t14_missing_metadata.py` | Missing metadata | Finalized |
| `tests/decision_context/test_t18_timestamp.py` | Timestamp in context | Finalized |
| `tests/decision_context/test_t24_decision_context_fields.py` | Context all fields | Finalized |
| `tests/security_posture/test_t19_risk_tier.py` | Risk tier metadata | Finalized |
| `tests/security_posture/test_t20_allowed_tools.py` | Allowed tools | Finalized |
| `tests/security_posture/test_t21_governance_tags.py` | Governance tags | Finalized |
| `tests/error_handling/test_t22_null_db_client.py` | Null DB client | Finalized |
| `tests/error_handling/test_t25_response_structure.py` | Response structure | Finalized |
| `tests/jwt/test_issue_jwt.py` | JWT issuance tests | Finalized |
| `tests/stm/test_stm_interface.py` | STM interface tests | Finalized |

---

## 7. Review Status

| Review Item | Status | Notes |
|-------------|--------|-------|
| Requirement review | Finalized | Identity requirements defined and accepted |
| Architecture review | Finalized | Layered Identity Service architecture reviewed |
| Pseudocode review | Finalized | Validation and decision flow reviewed |
| Test case review | Finalized | All unit tests reviewed |
| Coding | Completed | All Phase 1 components implemented |
| Coding review | Completed | Code reviewed and finalized |
| Test execution | Completed | All tests passing |
| Gateway integration | Pending | End-to-end testing with Gateway |
| Security review | Pending | |
| Final sign-off | Not started | |
