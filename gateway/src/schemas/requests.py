from typing import Any

from pydantic import BaseModel, Field


class GatewayIdentityRequest(BaseModel):
    agent_id: str
    session_id: str
    environment: str
    tenant_id: str = "tenant-default"
    origin: str = "gateway"
    network_zone: str = "internal"


class GatewayPlanRequest(GatewayIdentityRequest):
    request_type: str = "plan"
    plan_id: str | None = None
    goal: str | None = None
    steps: list[dict[str, Any]] = Field(default_factory=list)


class GatewayToolCallRequest(GatewayIdentityRequest):
    request_type: str = "tool_call"
    tool_name: str
    action: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class GatewayIORequest(GatewayIdentityRequest):
    request_type: str = "io"
    io_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
