"""
Core schemas for Identity Agent
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


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
    ownership_team: str
    registered_at: datetime
    updated_at: datetime


class AgentMetadata(BaseModel):
    agent_id: str
    role: str
    risk_tier: str
    autonomy_level: str
    allowed_tools: List[str]
    capabilities: List[str]
    governance_tags: List[str]
    updated_at: datetime


class AuditLogEvent(BaseModel):
    event_id: str
    timestamp: datetime
    agent_id: str
    session_id: str
    tenant_id: str
    environment: str
    origin: str
    network_zone: str
    event_type: str
    decision: str
    reason: str
    hash: Optional[str] = None
    tamper_proof_ref: Optional[str] = None


class IdentityDecisionContext(BaseModel):
    agent_id: str
    tenant_id: str
    environment: str
    network_zone: str
    origin: str
    session_id: str
    metadata: AgentMetadata
    status: str
    timestamp: datetime


class FinalResponse(BaseModel):
    success: bool
    decision_context: Optional[IdentityDecisionContext] = None
    audit_event_id: Optional[str] = None
    error_message: Optional[str] = None