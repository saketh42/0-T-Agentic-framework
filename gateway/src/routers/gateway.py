from fastapi import APIRouter

from gateway.src.schemas.requests import (
    GatewayIdentityRequest,
    GatewayIORequest,
    GatewayPlanRequest,
    GatewayToolCallRequest,
)
from gateway.src.services.gateway_service import (
    handle_identity_check,
    handle_io_check,
    handle_plan_check,
    handle_tool_call_check,
)


router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "security-privacy-gateway"
    }


@router.post("/check_identity")
def check_identity(payload: GatewayIdentityRequest):
    return handle_identity_check(payload).model_dump()


@router.post("/check_plan")
def check_plan(payload: GatewayPlanRequest):
    return handle_plan_check(payload).model_dump()


@router.post("/check_tool_call")
def check_tool_call(payload: GatewayToolCallRequest):
    return handle_tool_call_check(payload).model_dump()


@router.post("/check_io")
def check_io(payload: GatewayIORequest):
    return handle_io_check(payload).model_dump()
