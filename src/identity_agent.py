"""
Identity Agent - Main Orchestrator

Wires all steps together in the correct sequence.
"""

from typing import Dict, Any, Optional
from schemas import FinalResponse

from validate_request import validate_request, validate_required_fields
from connect_db import connect_to_database
from check_registry import check_registry
from fetch_metadata import fetch_metadata
from build_decision_context import build_decision_context
from send_to_policy_agent import send_to_policy_agent, create_allow_audit_log


def identity_agent_flow(
    request_payload: Dict[str, Any],
    db_client=None
) -> FinalResponse:
    """
    Main Identity Agent flow.
    
    Steps:
    1. Validate request
    2. Connect to database
    3. Check registry
    4. Fetch metadata
    5. Build decision context
    6. Send to Policy Agent
    
    Returns:
        FinalResponse with decision context or error
    """
    print("\n" + "="*60)
    print("🔐 IDENTITY AGENT FLOW STARTED")
    print("="*60)
    
    # Step 1: Validate Request
    print("\n>>> Step 1: Validate Request")
    request, error = validate_request(request_payload)
    if error:
        print("   ❌ Step 1 FAILED")
        return error
    
    field_error = validate_required_fields(request)
    if field_error:
        print("   ❌ Step 1 FAILED - Required fields")
        return field_error
    print("   ✅ Step 1 PASSED")
    
    # Step 2: Connect to Database
    print("\n>>> Step 2: Connect to Database")
    db, db_error = connect_to_database(db_client)
    if db_error:
        print("   ❌ Step 2 FAILED")
        return db_error
    print("   ✅ Step 2 PASSED")
    
    # Step 3: Check Registry
    print("\n>>> Step 3: Check Registry")
    registry_record, status, reg_error, deny_audit = check_registry(request, db)
    if reg_error:
        # Write deny audit log
        try:
            db.write_audit_log(deny_audit)
            print("   📝 Deny audit log written to DB")
        except Exception as e:
            print(f"   ⚠️ Failed to write audit log: {e}")
        print("   ❌ Step 3 FAILED")
        return FinalResponse(
            success=False,
            error_message=reg_error.error_message,
            audit_event_id=deny_audit.event_id
        )
    print("   ✅ Step 3 PASSED")
    
    # Step 4: Fetch Metadata
    print("\n>>> Step 4: Fetch Metadata")
    metadata, meta_error = fetch_metadata(request.agent_id, db)
    if meta_error:
        print("   ❌ Step 4 FAILED")
        return meta_error
    print("   ✅ Step 4 PASSED")
    
    # Step 5: Build Decision Context
    print("\n>>> Step 5: Build Decision Context")
    decision_context = build_decision_context(request, metadata, status)
    print("   ✅ Step 5 PASSED")
    
    # Step 6: Send to Policy Agent
    print("\n>>> Step 6: Send to Policy Agent")
    allow_audit, policy_error = send_to_policy_agent(request, decision_context)
    if policy_error:
        print("   ❌ Step 6 FAILED")
        return policy_error
    
    # Only write audit log for DENY cases (failure)
    # For ALLOW cases, decision context is sent to Policy Agent
    print("   ✅ Step 6 PASSED")
    print("   📝 No audit log for ALLOW - sent to Policy Agent")
    
    # Return success response
    print("\n" + "="*60)
    print("✅ IDENTITY AGENT FLOW COMPLETED - SUCCESS")
    print("="*60)
    
    return FinalResponse(
        success=True,
        decision_context=decision_context,
        audit_event_id=None  # No audit log for success - goes to Policy Agent
    )