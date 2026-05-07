"""
Database client interface for Identity Agent
"""

from typing import Optional
from abc import ABC, abstractmethod

from schemas import AgentRegistryRecord, AgentSecurityMetadata, IdentityAgentAuditLogEvent


class IdentityAgentDatabaseClient(ABC):
    
    @abstractmethod
    def fetch_from_registry_active(self, agent_id: str) -> Optional[AgentRegistryRecord]:
        pass
    
    @abstractmethod
    def fetch_from_registry_suspended(self, agent_id: str) -> Optional[AgentRegistryRecord]:
        pass
    
    @abstractmethod
    def fetch_from_registry_disabled(self, agent_id: str) -> Optional[AgentRegistryRecord]:
        pass
    
    @abstractmethod
    def fetch_from_registry_pending(self, agent_id: str) -> Optional[AgentRegistryRecord]:
        pass
    
    @abstractmethod
    def fetch_agent_metadata(self, agent_id: str) -> Optional[AgentSecurityMetadata]:
        pass
    
    @abstractmethod
    def write_audit_log(self, log_event: IdentityAgentAuditLogEvent) -> bool:
        pass