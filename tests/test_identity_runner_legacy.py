"""
Identity Agent Test Runner (Standalone)

Run: python3 test_identity_runner.py

Uses test_data/*.json for test inputs and mock data.
"""

import sys
import os
import json
from datetime import datetime
from unittest.mock import Mock

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pseudocode"))

from identity_agent import (
    IdentityRequest,
    RegistryRecord,
    AgentMetadata,
    AuditLogEvent,
    IdentityDecisionContext,
    FinalResponse,
    DatabaseClient,
    identity_agent_flow
)


def load_json(filename):
    """Load JSON data from test_data directory"""
    path = os.path.join(TEST_DATA_DIR, filename)
    with open(path, 'r') as f:
        return json.load(f)


TEST_INPUTS = load_json("identity_agent_inputs.json")
MOCK_DATA = load_json("identity_agent_mocks.json")


def parse_dt(dt_str):
    """Parse ISO datetime string"""
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))


def create_registry_record(data):
    """Create RegistryRecord from mock data"""
    return RegistryRecord(
        agent_id=data["agent_id"],
        tenant_id=data["tenant_id"],
        environment=data["environment"],
        ownership_team=data["ownership_team"],
        registered_at=parse_dt(data["registered_at"]),
        updated_at=parse_dt(data["updated_at"])
    )


def create_metadata(agent_id, data):
    """Create AgentMetadata from mock data"""
    return AgentMetadata(
        agent_id=agent_id,
        role=data["role"],
        risk_tier=data["risk_tier"],
        autonomy_level=data["autonomy_level"],
        allowed_tools=data["allowed_tools"],
        capabilities=data["capabilities"],
        governance_tags=data["governance_tags"],
        updated_at=parse_dt(data["updated_at"])
    )


def create_mock_db_client_for_status(agent_id, status, has_metadata=True):
    """Create mock DB client for a specific agent status"""
    mock = Mock(spec=DatabaseClient)
    mock.fetch_from_registry_active = Mock(return_value=None)
    mock.fetch_from_registry_suspended = Mock(return_value=None)
    mock.fetch_from_registry_disabled = Mock(return_value=None)
    mock.fetch_from_registry_pending = Mock(return_value=None)
    mock.fetch_agent_metadata = Mock(return_value=None)
    mock.write_audit_log = Mock(return_value=True)

    registry_data = MOCK_DATA["registry_records"].get(agent_id, {}).get(status)
    if registry_data:
        record = create_registry_record(registry_data)
        if status == "active":
            mock.fetch_from_registry_active.return_value = record
        elif status == "suspended":
            mock.fetch_from_registry_suspended.return_value = record
        elif status == "disabled":
            mock.fetch_from_registry_disabled.return_value = record
        elif status == "pending":
            mock.fetch_from_registry_pending.return_value = record

    if has_metadata:
        metadata_data = MOCK_DATA["metadata"].get(agent_id)
        if metadata_data:
            mock.fetch_agent_metadata.return_value = create_metadata(agent_id, metadata_data)

    return mock


def create_mock_db_with_record(record, has_metadata=True):
    """Create mock DB client with a specific registry record"""
    mock = Mock(spec=DatabaseClient)
    mock.fetch_from_registry_active = Mock(return_value=None)
    mock.fetch_from_registry_suspended = Mock(return_value=None)
    mock.fetch_from_registry_disabled = Mock(return_value=None)
    mock.fetch_from_registry_pending = Mock(return_value=None)
    mock.fetch_agent_metadata = Mock(return_value=None)
    mock.write_audit_log = Mock(return_value=True)

    if record:
        mock.fetch_from_registry_active.return_value = record

    if has_metadata:
        metadata_data = MOCK_DATA["metadata"].get(record.agent_id)
        if metadata_data:
            mock.fetch_agent_metadata.return_value = create_metadata(record.agent_id, metadata_data)

    return mock


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def add(self, test_name, passed, message=""):
        status = "PASS" if passed else "FAIL"
        self.results.append(f"[{status}] {test_name}")
        if message:
            self.results.append(f"       {message}")
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def summary(self):
        return f"\n{'='*50}\nRESULTS: {self.passed} passed, {self.failed} failed\n{'='*50}\n" + "\n".join(self.results)


def test_t01_valid_request_returns_success(results):
    """T01: Valid request, active agent, valid metadata"""
    payload = TEST_INPUTS["requests"]["valid_request"]
    mock_db = create_mock_db_client_for_status("agent-001", "active")
    result = identity_agent_flow(payload, mock_db)
    
    passed = (
        result.success is True and
        result.decision_context is not None and
        result.decision_context.agent_id == "agent-001" and
        result.decision_context.status == "active"
    )
    
    results.add("T01: Valid request returns success", passed, 
                f"decision_context={result.decision_context is not None}" if not passed else "")


def test_t02_missing_agent_id(results):
    """T02: Missing agent_id"""
    payload = TEST_INPUTS["requests"]["missing_agent_id"]
    mock_db = create_mock_db_client_for_status("agent-001", "active")
    result = identity_agent_flow(payload, mock_db)
    
    passed = result.success is False and "agent_id" in result.error_message.lower()
    results.add("T02: Missing agent_id returns error", passed, result.error_message)


def test_t03_empty_agent_id(results):
    """T03: Empty agent_id"""
    payload = TEST_INPUTS["requests"]["empty_agent_id"]
    mock_db = create_mock_db_client_for_status("agent-001", "active")
    result = identity_agent_flow(payload, mock_db)
    
    passed = result.success is False and "agent_id" in result.error_message.lower()
    results.add("T03: Empty agent_id returns error", passed)


def test_t04_missing_tenant_id(results):
    """T04: Missing tenant_id"""
    payload = TEST_INPUTS["requests"]["missing_tenant_id"]
    mock_db = create_mock_db_client_for_status("agent-001", "active")
    result = identity_agent_flow(payload, mock_db)
    
    passed = result.success is False and "tenant_id" in result.error_message.lower()
    results.add("T04: Missing tenant_id returns error", passed)


def test_t05_missing_environment(results):
    """T05: Missing environment"""
    payload = TEST_INPUTS["requests"]["missing_environment"]
    mock_db = create_mock_db_client_for_status("agent-001", "active")
    result = identity_agent_flow(payload, mock_db)
    
    passed = result.success is False and "environment" in result.error_message.lower()
    results.add("T05: Missing environment returns error", passed)


def test_t06_whitespace_agent_id(results):
    """T06: Whitespace-only agent_id"""
    payload = TEST_INPUTS["requests"]["whitespace_agent_id"]
    mock_db = create_mock_db_client_for_status("agent-001", "active")
    result = identity_agent_flow(payload, mock_db)
    
    passed = result.success is False and "agent_id" in result.error_message.lower()
    results.add("T06: Whitespace agent_id returns error", passed)


def test_t07_invalid_json_payload(results):
    """T07: Invalid JSON payload"""
    mock_db = create_mock_db_client_for_status("agent-001", "active")
    result = identity_agent_flow("not valid json", mock_db)
    
    passed = result.success is False and "invalid" in result.error_message.lower()
    results.add("T07: Invalid JSON returns error", passed)


def test_t08_unknown_agent(results):
    """T08: Agent not in registry"""
    mock_db = Mock(spec=DatabaseClient)
    mock_db.fetch_from_registry_active = Mock(return_value=None)
    mock_db.fetch_from_registry_suspended = Mock(return_value=None)
    mock_db.fetch_from_registry_disabled = Mock(return_value=None)
    mock_db.fetch_from_registry_pending = Mock(return_value=None)
    mock_db.fetch_agent_metadata = Mock(return_value=None)
    mock_db.write_audit_log = Mock(return_value=True)
    
    payload = TEST_INPUTS["requests"]["unknown_agent"]
    result = identity_agent_flow(payload, mock_db)
    
    passed = result.success is False and "unknown agent" in result.error_message.lower()
    results.add("T08: Unknown agent returns error", passed, result.error_message if not passed else "")


def test_t09_cross_tenant(results):
    """T09: Cross-tenant access attempt"""
    mock_db = Mock(spec=DatabaseClient)
    
    record_data = MOCK_DATA["cross_tenant_record"]
    registry_record = create_registry_record(record_data)
    
    mock_db.fetch_from_registry_active = Mock(return_value=registry_record)
    mock_db.fetch_from_registry_suspended = Mock(return_value=None)
    mock_db.fetch_from_registry_disabled = Mock(return_value=None)
    mock_db.fetch_from_registry_pending = Mock(return_value=None)
    mock_db.fetch_agent_metadata = Mock(return_value=None)
    mock_db.write_audit_log = Mock(return_value=True)
    
    payload = TEST_INPUTS["requests"]["cross_tenant"]
    result = identity_agent_flow(payload, mock_db)
    
    passed = result.success is False and "cross-tenant" in result.error_message.lower()
    results.add("T09: Cross-tenant access denied", passed, result.error_message if not passed else "")


def test_t10_cross_environment(results):
    """T10: Cross-environment access attempt"""
    mock_db = Mock(spec=DatabaseClient)
    
    record_data = MOCK_DATA["cross_environment_record"]
    registry_record = create_registry_record(record_data)
    
    mock_db.fetch_from_registry_active = Mock(return_value=registry_record)
    mock_db.fetch_from_registry_suspended = Mock(return_value=None)
    mock_db.fetch_from_registry_disabled = Mock(return_value=None)
    mock_db.fetch_from_registry_pending = Mock(return_value=None)
    mock_db.fetch_agent_metadata = Mock(return_value=None)
    mock_db.write_audit_log = Mock(return_value=True)
    
    payload = TEST_INPUTS["requests"]["cross_environment"]
    result = identity_agent_flow(payload, mock_db)
    
    passed = result.success is False and "cross-environment" in result.error_message.lower()
    results.add("T10: Cross-environment access denied", passed, result.error_message if not passed else "")


def test_t11_suspended_status(results):
    """T11: Agent status = suspended"""
    payload = TEST_INPUTS["requests"]["suspended_agent"]
    mock_db = create_mock_db_client_for_status("agent-001", "suspended")
    result = identity_agent_flow(payload, mock_db)
    
    passed = result.success is False and "suspended" in result.error_message.lower()
    results.add("T11: Suspended agent denied", passed, result.error_message if not passed else "")


def test_t12_disabled_status(results):
    """T12: Agent status = disabled"""
    payload = TEST_INPUTS["requests"]["disabled_agent"]
    mock_db = create_mock_db_client_for_status("agent-001", "disabled")
    result = identity_agent_flow(payload, mock_db)
    
    passed = result.success is False and "disabled" in result.error_message.lower()
    results.add("T12: Disabled agent denied", passed, result.error_message if not passed else "")


def test_t13_pending_status(results):
    """T13: Agent status = pending"""
    payload = TEST_INPUTS["requests"]["pending_agent"]
    mock_db = create_mock_db_client_for_status("agent-001", "pending")
    result = identity_agent_flow(payload, mock_db)
    
    passed = result.success is False and "pending" in result.error_message.lower()
    results.add("T13: Pending agent denied", passed, result.error_message if not passed else "")


def test_t14_missing_metadata(results):
    """T14: Active agent but no metadata"""
    payload = TEST_INPUTS["requests"]["missing_metadata"]
    mock_db = create_mock_db_client_for_status("agent-001", "active", has_metadata=False)
    result = identity_agent_flow(payload, mock_db)
    
    passed = result.success is False and "missing metadata" in result.error_message.lower()
    results.add("T14: Missing metadata returns error", passed, result.error_message if not passed else "")


def test_t15_audit_log_on_success(results):
    """T15: Audit log written on success"""
    payload = TEST_INPUTS["requests"]["valid_request"]
    mock_db = create_mock_db_client_for_status("agent-001", "active")
    result = identity_agent_flow(payload, mock_db)
    
    passed = mock_db.write_audit_log.called
    results.add("T15: Audit log written on success", passed)
    
    if passed:
        audit_log = mock_db.write_audit_log.call_args[0][0]
        passed2 = audit_log.decision == "ALLOW"
        results.add("T15b: Audit decision is ALLOW", passed2)


def test_t16_audit_log_on_denial(results):
    """T16: Audit log written on denial"""
    payload = TEST_INPUTS["requests"]["suspended_agent"]
    mock_db = create_mock_db_client_for_status("agent-001", "suspended")
    result = identity_agent_flow(payload, mock_db)
    
    passed = mock_db.write_audit_log.called
    results.add("T16: Audit log written on denial", passed)
    
    if passed:
        audit_log = mock_db.write_audit_log.call_args[0][0]
        passed2 = audit_log.decision == "DENY"
        results.add("T16b: Audit decision is DENY", passed2)


def test_t17_audit_log_required_fields(results):
    """T17: Audit log has all required fields"""
    payload = TEST_INPUTS["requests"]["valid_request"]
    mock_db = create_mock_db_client_for_status("agent-001", "active")
    result = identity_agent_flow(payload, mock_db)
    
    if not mock_db.write_audit_log.called:
        results.add("T17: Audit log written", False, "write_audit_log was not called")
        return
        
    audit_log = mock_db.write_audit_log.call_args[0][0]
    
    required_fields = ["event_id", "timestamp", "agent_id", "session_id", 
                  "tenant_id", "environment", "origin", "network_zone",
                  "event_type", "decision", "reason"]
    
    all_present = all(hasattr(audit_log, f) and getattr(audit_log, f) is not None 
                      for f in required_fields)
    
    results.add("T17: Audit log has all required fields", all_present)


def test_t18_decision_context_timestamp(results):
    """T18: Decision context has timestamp"""
    payload = TEST_INPUTS["requests"]["valid_request"]
    mock_db = create_mock_db_client_for_status("agent-001", "active")
    result = identity_agent_flow(payload, mock_db)
    
    passed = result.decision_context.timestamp is not None
    results.add("T18: Decision context has timestamp", passed)


def test_t19_security_posture_risk_tier(results):
    """T19: Security posture - risk_tier passed through"""
    payload = TEST_INPUTS["requests"]["high_risk_agent"]
    mock_db = create_mock_db_client_for_status("agent-highrisk", "active")
    result = identity_agent_flow(payload, mock_db)
    
    if not result.success or not result.decision_context:
        results.add("T19: Security posture - risk_tier passed through", False, "Request failed")
        return
        
    passed = (result.decision_context.metadata.risk_tier == "critical" and
              result.decision_context.metadata.autonomy_level == "autonomous")
    results.add("T19: Security posture - risk_tier passed through", passed)


def test_t20_security_posture_allowed_tools(results):
    """T20: Security posture - allowed_tools passed through"""
    payload = TEST_INPUTS["requests"]["high_risk_agent"]
    mock_db = create_mock_db_client_for_status("agent-highrisk", "active")
    result = identity_agent_flow(payload, mock_db)
    
    if not result.success or not result.decision_context:
        results.add("T20: Security posture - allowed_tools passed through", False, "Request failed")
        return
    
    expected_tools = ["containment", "quarantine", "block_ip"]
    actual_tools = result.decision_context.metadata.allowed_tools
    
    passed = set(expected_tools) == set(actual_tools)
    results.add("T20: Security posture - allowed_tools passed through", passed)


def test_t21_security_posture_governance_tags(results):
    """T21: Security posture - governance_tags passed through"""
    payload = TEST_INPUTS["requests"]["high_risk_agent"]
    mock_db = create_mock_db_client_for_status("agent-highrisk", "active")
    result = identity_agent_flow(payload, mock_db)
    
    if not result.success or not result.decision_context:
        results.add("T21: Security posture - governance_tags passed through", False, "Request failed")
        return
    
    expected_tags = ["pci", "hipaa", "fedramp"]
    actual_tags = result.decision_context.metadata.governance_tags
    
    passed = set(expected_tags) == set(actual_tags)
    results.add("T21: Security posture - governance_tags passed through", passed)


def test_t22_null_db_client(results):
    """T22: Null database client returns error"""
    payload = TEST_INPUTS["requests"]["valid_request"]
    result = identity_agent_flow(payload, db_client=None)
    
    passed = result.success is False and "database" in result.error_message.lower()
    results.add("T22: Null db_client returns error", passed)


def test_t23_audit_log_event_id_unique(results):
    """T23: Audit log event_id is unique per request"""
    payload = TEST_INPUTS["requests"]["valid_request"]
    mock_db = create_mock_db_client_for_status("agent-001", "active")
    
    result1 = identity_agent_flow(payload, mock_db)
    result2 = identity_agent_flow(payload, mock_db)
    
    if not result1.audit_event_id or not result2.audit_event_id:
        results.add("T23: Audit log event_id is unique", False, "Missing event_id")
        return
    
    passed = result1.audit_event_id != result2.audit_event_id
    results.add("T23: Audit log event_id is unique", passed)


def test_t24_decision_context_has_all_fields(results):
    """T24: Decision context has all required fields"""
    payload = TEST_INPUTS["requests"]["valid_request"]
    mock_db = create_mock_db_client_for_status("agent-001", "active")
    result = identity_agent_flow(payload, mock_db)
    
    if not result.decision_context:
        results.add("T24: Decision context has all fields", False, "No decision context")
        return
    
    required_fields = ["agent_id", "tenant_id", "environment", "network_zone",
                      "origin", "session_id", "metadata", "status", "timestamp"]
    
    all_present = all(hasattr(result.decision_context, f) and 
                      getattr(result.decision_context, f) is not None 
                      for f in required_fields)
    
    results.add("T24: Decision context has all required fields", all_present)


def test_t25_response_structure(results):
    """T25: FinalResponse has correct structure"""
    payload = TEST_INPUTS["requests"]["valid_request"]
    mock_db = create_mock_db_client_for_status("agent-001", "active")
    result = identity_agent_flow(payload, mock_db)
    
    if result.success:
        passed = (result.decision_context is not None and 
                  result.audit_event_id is not None and
                  result.error_message is None)
    else:
        passed = (result.decision_context is None and
                  result.error_message is not None and
                  result.audit_event_id is not None)
    
    results.add("T25: FinalResponse has correct structure", passed)


def main():
    print("=" * 50)
    print("Identity Agent Test Suite")
    print("=" * 50)
    print(f"Loaded {len(TEST_INPUTS['requests'])} test requests from JSON")
    print(f"Loaded {len(MOCK_DATA['registry_records'])} registry records from JSON")
    print(f"Loaded {len(MOCK_DATA['metadata'])} metadata records from JSON")
    print()
    
    results = TestResults()
    
    test_t01_valid_request_returns_success(results)
    test_t02_missing_agent_id(results)
    test_t03_empty_agent_id(results)
    test_t04_missing_tenant_id(results)
    test_t05_missing_environment(results)
    test_t06_whitespace_agent_id(results)
    test_t07_invalid_json_payload(results)
    test_t08_unknown_agent(results)
    test_t09_cross_tenant(results)
    test_t10_cross_environment(results)
    test_t11_suspended_status(results)
    test_t12_disabled_status(results)
    test_t13_pending_status(results)
    test_t14_missing_metadata(results)
    test_t15_audit_log_on_success(results)
    test_t16_audit_log_on_denial(results)
    test_t17_audit_log_required_fields(results)
    test_t18_decision_context_timestamp(results)
    test_t19_security_posture_risk_tier(results)
    test_t20_security_posture_allowed_tools(results)
    test_t21_security_posture_governance_tags(results)
    test_t22_null_db_client(results)
    test_t23_audit_log_event_id_unique(results)
    test_t24_decision_context_has_all_fields(results)
    test_t25_response_structure(results)
    
    print(results.summary())
    
    sys.exit(0 if results.failed == 0 else 1)


if __name__ == "__main__":
    main()