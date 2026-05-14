"""
Database client interface for Identity Agent
"""

from typing import Optional, List
from abc import ABC, abstractmethod

from schemas import AgentRegistryRecord, AgentSecurityMetadata, IdentityAgentAuditLogEvent, SigningKey


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
    def fetch_agent_security_metadata(self, agent_id: str) -> Optional[AgentSecurityMetadata]:
        pass
    
    @abstractmethod
    def write_audit_log(self, log_event: IdentityAgentAuditLogEvent) -> bool:
        pass

    @abstractmethod
    def get_active_signing_key(self) -> Optional[SigningKey]:
        pass

    @abstractmethod
    def get_signing_key_by_kid(self, kid: str) -> Optional[SigningKey]:
        pass

    @abstractmethod
    def insert_signing_key(self, key: SigningKey) -> bool:
        pass

    @abstractmethod
    def list_active_signing_keys(self) -> List[SigningKey]:
        pass
