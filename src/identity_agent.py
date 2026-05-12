"""
Identity Agent - Main Orchestrator

Wires all steps together in the correct sequence.
"""

from typing import Dict, Any, Optional
from schemas import IdentityValidationResponse

from validate_request import validate_identity_validation_request, validate_required_request_fields
from connect_db import establish_identity_agent_db_connection
from check_registry import lookup_agent_in_identity_registry, create_identity_deny_audit_log
from fetch_metadata import fetch_agent_security_metadata
from build_decision_context import build_identity_decision_context
from send_to_policy_agent import submit_decision_context_to_gateway, create_identity_allow_audit_log
from issue_jwt import issue_agent_jwt


def identity_agent_service(
    request_payload: Dict[str, Any],
    db_client=None,
    stm_client=None
) -> IdentityValidationResponse:
    """
    Identity & Context Service - Main entry point.
    
    Steps:
    1. Validate request
    2. Connect to database
    3. Lookup agent in registry
    4. Fetch agent metadata
    5. Build decision context
    6. Submit to Gateway
    
    Returns:
        FinalResponse with decision context or error
    """
    print("\n" + "="*60)
    print("IDENTITY SERVICE STARTED")
    print("="*60)
    
    # Step 1: Validate Request
    print("\n>>> Step 1: Validate Request")
    request, error = validate_identity_validation_request(request_payload)
    if error:
        print("    Step 1 FAILED")
        return error
    
    field_error = validate_required_request_fields(request)
    if field_error:
        print("    Step 1 FAILED - Required fields")
        return field_error
    print("    Step 1 PASSED")
    
    # Step 2: Connect to Database
    print("\n>>> Step 2: Connect to Database")
    db, db_error = establish_identity_agent_db_connection(db_client)
    if db_error:
        print("   [FAIL] Step 2 FAILED")
        return db_error
    print("   [PASS] Step 2 PASSED")
    
    # Step 3: Lookup Agent in Registry
    print("\n>>> Step 3: Lookup Agent in Registry")
    registry_record, status, reg_error, deny_audit = lookup_agent_in_identity_registry(request, db)
    if reg_error:
        # Write deny audit log
        try:
            db.write_audit_log(deny_audit)
            print("   [AUDIT] Deny audit log written to DB")
        except Exception as e:
            print(f"   [WARN] Failed to write audit log: {e}")
        print("   [FAIL] Step 3 FAILED")
        return IdentityValidationResponse(
            is_authorized=False,
            failure_reason=reg_error.failure_reason,
            audit_log_id=deny_audit.event_id
        )
    print("   [PASS] Step 3 PASSED")
    
    # Step 4: Fetch Agent Metadata
    print("\n>>> Step 4: Fetch Agent Metadata")
    metadata, meta_error = fetch_agent_security_metadata(request.agent_id, db)
    if meta_error:
        print("   [FAIL] Step 4 FAILED")
        return meta_error
    print("   [PASS] Step 4 PASSED")
    
    # Optional: Initialize STM session (does not break flow if fails)
    if stm_client:
        try:
            stm_client.create_session(
                session_id=request.session_id,
                agent_id=request.agent_id,
                tenant_id=request.tenant_id,
                current_goal=""
            )
            print("   [AUDIT] STM session initialized (empty)")
        except Exception as e:
            print(f"   [WARN] STM init failed (non-critical): {e}")
    
    # Step 5: Build Decision Context
    print("\n>>> Step 5: Build Decision Context")
    decision_context = build_identity_decision_context(request, metadata, status)
    print("   [PASS] Step 5 PASSED")
    
    # Step 5b: Issue JWT
    print("\n>>> Step 5b: Issue JWT Token")
    try:
        token = issue_agent_jwt(decision_context)
        decision_context.token = token
        print("   [PASS] JWT issued successfully")
        print(f"   Token: {token[:80]}...")
    except Exception as e:
        print(f"   [FAIL] JWT issuance failed: {e}")
        return IdentityValidationResponse(
            is_authorized=False,
            failure_reason=f"JWT issuance failed: {str(e)}"
        )
    
    # Step 6: Submit to Gateway
    print("\n>>> Step 6: Submit to Gateway")
    allow_audit, gateway_error = submit_decision_context_to_gateway(request, decision_context)
    if gateway_error:
        print("   [FAIL] Step 6 FAILED")
        return policy_error
    
    # Only write audit log for DENY cases (failure)
    # For ALLOW cases, decision context is submitted to Gateway
    print("   [PASS] Step 6 PASSED")
    print("   [AUDIT] No audit log for ALLOW - submitted to Gateway")
    
    # Return success response
    print("\n" + "="*60)
    print("[PASS] IDENTITY SERVICE COMPLETED - SUCCESS")
    print("="*60)
    
    return IdentityValidationResponse(
        is_authorized=True,
        identity_context=decision_context,
        audit_log_id=None  # No audit log for success - goes to Gateway
    )