"""
Core schemas for Identity Agent
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class IdentityValidationRequest(BaseModel):
    agent_id: str
    tenant_id: str
    environment: str
    session_id: str
    origin: str
    network_zone: str
    auth_token: Optional[str] = None


class AgentRegistryRecord(BaseModel):
    agent_id: str
    tenant_id: str
    name: str
    environment: Optional[str] = None
    type: Optional[str] = None
    purpose: Optional[str] = None
    role: Optional[str] = None
    status: str
    risk_tier: Optional[str] = None
    autonomy_level: Optional[str] = None
    ownership_team: Optional[str] = None
    governance_tags: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AgentSecurityMetadata(BaseModel):
    agent_id: str
    name: str
    role: str
    risk_tier: str
    autonomy_level: str
    allowed_tools: List[str]
    capabilities: List[str]
    governance_tags: List[str]
    updated_at: Optional[datetime] = None


class IdentityAgentAuditLogEvent(BaseModel):
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


class AgentIdentityDecisionContext(BaseModel):
    agent_id: str
    tenant_id: str
    environment: str
    network_zone: str
    origin: str
    session_id: str
    metadata: AgentSecurityMetadata
    status: str
    timestamp: datetime
    token: Optional[str] = None


class IdentityValidationResponse(BaseModel):
    authorization: str
    identity_context: Optional[AgentIdentityDecisionContext] = None
    failure_reason: Optional[str] = None


class SigningKey(BaseModel):
    kid: str
    private_key_pem: str
    public_key_pem: str
    algorithm: str = "RS256"
    active: bool = True
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class AgentShortTermMemorySession(BaseModel):
    session_id: str
    agent_id: str
    tenant_id: str
    current_goal: str
    current_plan: List[str] = []
    intermediate_steps: List[str] = []
    recent_tool_outputs: List[str] = []
    flags: Dict[str, Any] = {}
    last_updated: str
