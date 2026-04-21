"""
Core schemas for Identity Agent

Pydantic models defining the data contracts - request and response structures.
Based on pseudocode/identity_agent.py
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class IdentityRequest(BaseModel):
    """Request schema for identity validation (API input)"""
    agent_id: str
    tenant_id: str
    environment: str
    session_id: str
    origin: str
    network_zone: str


class RegistryRecord(BaseModel):
    """
    Registry record schema.
    Stored in tables: registry_active, registry_suspended, registry_disabled, registry_pending
    """
    agent_id: str
    tenant_id: str
    environment: str
    ownership_team: str
    registered_at: datetime
    updated_at: datetime


class AgentMetadata(BaseModel):
    """
    Agent metadata defining security posture.
    
    Fields:
    - role: Agent role (planner, worker, governance)
    - risk_tier: Risk level (low, medium, high, critical)
    - autonomy_level: Authorized autonomy (supervised, autonomous)
    - allowed_tools: Tool names agent can invoke
    - capabilities: Agent capabilities
    - governance_tags: Compliance tags
    """
    agent_id: str
    role: str
    risk_tier: str
    autonomy_level: str
    allowed_tools: List[str]
    capabilities: List[str]
    governance_tags: List[str]
    updated_at: datetime


class AuditLogEvent(BaseModel):
    """Audit log event schema"""
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
    """
    Output contract: Passed to Policy Agent for authorization.
    Contains agent identity + context + security posture.
    """
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
    """Final response schema"""
    success: bool
    decision_context: Optional[IdentityDecisionContext] = None
    audit_event_id: Optional[str] = None
    error_message: Optional[str] = None