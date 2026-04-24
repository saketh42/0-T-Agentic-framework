"""
PostgreSQL Database Client for Identity Agent

Implements the DatabaseClient interface using psycopg2.
"""

import os
from typing import Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from .schemas import RegistryRecord, AgentMetadata, AuditLogEvent
from .database import DatabaseClient


class PostgresDatabaseClient(DatabaseClient):
    """PostgreSQL implementation of DatabaseClient"""
    
    def __init__(self):
        self.connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres")
        )
    
    def _execute(self, query: str, params: tuple = None):
        """Execute a query and return results"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def _execute_all(self, query: str, params: tuple = None):
        """Execute a query and return all results"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def fetch_from_registry_active(self, agent_id: str) -> Optional[RegistryRecord]:
        query = """
            SELECT agent_id, tenant_id, environment, ownership_team, 
                   registered_at, updated_at
            FROM agents 
            WHERE agent_id = %s AND status = 'active'
        """
        result = self._execute(query, (agent_id,))
        if result:
            return RegistryRecord(
                agent_id=result['agent_id'],
                tenant_id=result['tenant_id'],
                environment=result['environment'],
                ownership_team=result['ownership_team'],
                registered_at=result['registered_at'],
                updated_at=result['updated_at']
            )
        return None
    
    def fetch_from_registry_suspended(self, agent_id: str) -> Optional[RegistryRecord]:
        query = """
            SELECT agent_id, tenant_id, environment, ownership_team,
                   registered_at, updated_at
            FROM agents 
            WHERE agent_id = %s AND status = 'suspended'
        """
        result = self._execute(query, (agent_id,))
        if result:
            return RegistryRecord(
                agent_id=result['agent_id'],
                tenant_id=result['tenant_id'],
                environment=result['environment'],
                ownership_team=result['ownership_team'],
                registered_at=result['registered_at'],
                updated_at=result['updated_at']
            )
        return None
    
    def fetch_from_registry_disabled(self, agent_id: str) -> Optional[RegistryRecord]:
        query = """
            SELECT agent_id, tenant_id, environment, ownership_team,
                   registered_at, updated_at
            FROM agents 
            WHERE agent_id = %s AND status = 'disabled'
        """
        result = self._execute(query, (agent_id,))
        if result:
            return RegistryRecord(
                agent_id=result['agent_id'],
                tenant_id=result['tenant_id'],
                environment=result['environment'],
                ownership_team=result['ownership_team'],
                registered_at=result['registered_at'],
                updated_at=result['updated_at']
            )
        return None
    
    def fetch_from_registry_pending(self, agent_id: str) -> Optional[RegistryRecord]:
        query = """
            SELECT agent_id, tenant_id, environment, ownership_team,
                   registered_at, updated_at
            FROM agents 
            WHERE agent_id = %s AND status = 'pending'
        """
        result = self._execute(query, (agent_id,))
        if result:
            return RegistryRecord(
                agent_id=result['agent_id'],
                tenant_id=result['tenant_id'],
                environment=result['environment'],
                ownership_team=result['ownership_team'],
                registered_at=result['registered_at'],
                updated_at=result['updated_at']
            )
        return None
    
    def fetch_agent_metadata(self, agent_id: str) -> Optional[AgentMetadata]:
        query = """
            SELECT agent_id, role, risk_tier, autonomy_level,
                   allowed_tools, capabilities, governance_tags, updated_at
            FROM agents 
            WHERE agent_id = %s AND status = 'active'
        """
        result = self._execute(query, (agent_id,))
        if result:
            return AgentMetadata(
                agent_id=result['agent_id'],
                role=result['role'],
                risk_tier=result['risk_tier'],
                autonomy_level=result['autonomy_level'],
                allowed_tools=result['allowed_tools'] or [],
                capabilities=result['capabilities'] or [],
                governance_tags=result['governance_tags'] or [],
                updated_at=result['updated_at']
            )
        return None
    
    def write_audit_log(self, log_event: AuditLogEvent) -> bool:
        query = """
            INSERT INTO audit_logs (
                log_id, timestamp, agent_id, session_id, tenant_id,
                environment, origin, network_zone, event_type,
                decision, reason
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (
                    log_event.event_id,
                    log_event.timestamp,
                    log_event.agent_id,
                    log_event.session_id,
                    log_event.tenant_id,
                    log_event.environment,
                    log_event.origin,
                    log_event.network_zone,
                    log_event.event_type,
                    log_event.decision,
                    log_event.reason
                ))
                self.connection.commit()
                return True
        except Exception as e:
            self.connection.rollback()
            raise e
    
    def close(self):
        """Close the database connection"""
        self.connection.close()