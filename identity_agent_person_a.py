from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# ==========================================
# SCHEMAS FOR DB TEAM (Person 1 Ownership)
# ==========================================


class IdentityRequest(BaseModel):
    agent_id: str
    tenant_id: str
    environment: str
    session_id: str
    origin: str
    network_zone: str


class RegistryRecord(BaseModel):
    agent_id: str
    tenant_id: str
    environment: str
    status: str
    ownership_team: str
    registered_at: datetime
    updated_at: datetime


class InitialValidationResponse(BaseModel):
    success: bool
    agent_id: Optional[str] = None
    registry_status: Optional[str] = None
    request_context: Optional[dict] = None
    error_message: Optional[str] = None


# ==========================================
# MOCK DATABASE INTERFACES
# ==========================================


class DatabaseClientPlaceholder:
    def fetch_registry_record(
        self,
        agent_id: str,
        tenant_id: str,
        environment: str,
    ) -> Optional[RegistryRecord]:
        # Implementation to be provided by DB Team
        pass


# ==========================================
# PERSON 1: INPUT VALIDATION + REGISTRY FLOW
# ==========================================


def person_a_identity_flow(
    request_payload: dict,
    db_client: DatabaseClientPlaceholder,
) -> InitialValidationResponse:
    """
    Executes Steps 1-2 for the Identity Agent (Person 1 Ownership)

    Step 1: Validate request
    Step 2: Look up agent in registry
    """

    # Step 1: Validate request shape and required fields
    try:
        request = IdentityRequest(**request_payload)
    except Exception as e:
        return InitialValidationResponse(
            success=False,
            error_message=f"Invalid request payload: {str(e)}",
        )

    if not request.agent_id.strip():
        return InitialValidationResponse(
            success=False,
            error_message="Invalid request: agent_id is required",
        )

    if not request.tenant_id.strip():
        return InitialValidationResponse(
            success=False,
            error_message="Invalid request: tenant_id is required",
        )

    if not request.environment.strip():
        return InitialValidationResponse(
            success=False,
            error_message="Invalid request: environment is required",
        )

    # Step 2: Look up agent in registry
    registry_record = db_client.fetch_registry_record(
        agent_id=request.agent_id,
        tenant_id=request.tenant_id,
        environment=request.environment,
    )

    # Unknown agent handling
    if not registry_record:
        return InitialValidationResponse(
            success=False,
            error_message=(
                f"Unknown agent: {request.agent_id} "
                f"for tenant={request.tenant_id}, environment={request.environment}"
            ),
        )

    # Return handoff payload for Person 2
    return InitialValidationResponse(
        success=True,
        agent_id=registry_record.agent_id,
        registry_status=registry_record.status,
        request_context={
            "tenant_id": request.tenant_id,
            "environment": request.environment,
            "session_id": request.session_id,
            "origin": request.origin,
            "network_zone": request.network_zone,
        },
    )

