"""
Step 1: Validate Request

Validates incoming request payload from Gateway.
"""

from typing import Dict, Any, Optional, Tuple
from schemas import IdentityRequest, FinalResponse


def validate_identity_request(request_payload: Dict[str, Any]) -> Tuple[Optional[IdentityRequest], Optional[FinalResponse]]:
    """
    Validates the incoming request payload.
    
    Returns:
        (IdentityRequest, None) on success
        (None, FinalResponse) on failure
    """
    print("\n" + "="*60)
    print(" STEP 1: VALIDATE REQUEST")
    print("="*60)
    print(f"\n   Input payload: {request_payload}")
    
    if not request_payload:
        error = FinalResponse(
            is_authorized=False,
            failure_reason="Empty request payload"
        )
        print("    Empty request payload")
        return None, error
    
    try:
        request = IdentityRequest(**request_payload)
        print("    Request parsed successfully")
        print(f"    agent_id: {request.agent_id}")
        print(f"    tenant_id: {request.tenant_id}")
        print(f"    environment: {request.environment}")
        return request, None
        
    except Exception as e:
        error = FinalResponse(
            is_authorized=False,
            failure_reason=f"Invalid request payload: {str(e)}"
        )
        print(f"    Invalid request: {str(e)}")
        return None, error


def validate_required_request_fields(request: IdentityRequest) -> Optional[FinalResponse]:
    """Validate required fields are not empty."""
    print("\n   Validating required fields...")
    
    if not request.agent_id or not request.agent_id.strip():
        error = FinalResponse(
            is_authorized=False,
            failure_reason="Invalid request: agent_id is required"
        )
        print("agent_id is empty")
        return error
    
    if not request.tenant_id or not request.tenant_id.strip():
        error = FinalResponse(
            is_authorized=False,
            failure_reason="Invalid request: tenant_id is required"
        )
        print("tenant_id is empty")
        return error
    
    if not request.environment or not request.environment.strip():
        error = FinalResponse(
            is_authorized=False,
            failure_reason="Invalid request: environment is required"
        )
        print("environment is empty")
        return error
    
    print("    All required fields validated")
    return None