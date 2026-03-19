from typing import Any

from pydantic import BaseModel, Field


class GatewayResponse(BaseModel):
    stage: str
    decision: str
    reason: str
    request_type: str
    identity: dict[str, Any] | None = None
    next_step: str | None = None
    notes: list[str] = Field(default_factory=list)
