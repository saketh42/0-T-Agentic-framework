"""
Database client interface for Identity Agent

Abstract interface for registry and audit log operations.
Implementation to be provided by DB Team.
"""

from typing import Optional
from abc import ABC, abstractmethod

from .schemas import RegistryRecord, AgentMetadata, AuditLogEvent


class DatabaseClient(ABC):
    """
    Abstract database client interface.
    
    Registry operations (separate tables per status):
    - fetch_from_registry_active
    - fetch_from_registry_suspended
    - fetch_from_registry_disabled
    - fetch_from_registry_pending
    
    Metadata operations:
    - fetch_agent_metadata
    
    Audit operations:
    - write_audit_log
    """
    
    @abstractmethod
    def fetch_from_registry_active(self, agent_id: str) -> Optional[RegistryRecord]:
        """Fetch agent from active registry table"""
        pass
    
    @abstractmethod
    def fetch_from_registry_suspended(self, agent_id: str) -> Optional[RegistryRecord]:
        """Fetch agent from suspended registry table"""
        pass
    
    @abstractmethod
    def fetch_from_registry_disabled(self, agent_id: str) -> Optional[RegistryRecord]:
        """Fetch agent from disabled registry table"""
        pass
    
    @abstractmethod
    def fetch_from_registry_pending(self, agent_id: str) -> Optional[RegistryRecord]:
        """Fetch agent from pending registry table"""
        pass
    
    @abstractmethod
    def fetch_agent_metadata(self, agent_id: str) -> Optional[AgentMetadata]:
        """Fetch agent metadata from metadata table"""
        pass
    
    @abstractmethod
    def write_audit_log(self, log_event: AuditLogEvent) -> bool:
        """Write audit log event (append-only, tamper-evident)"""
        pass