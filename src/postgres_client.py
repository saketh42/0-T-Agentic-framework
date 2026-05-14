"""
PostgreSQL Database Client for Identity Agent

Implements the DatabaseClient interface using psycopg2.
"""

import os
from typing import Optional, List
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from schemas import AgentRegistryRecord, AgentSecurityMetadata, SigningKey
from database import IdentityAgentDatabaseClient


class PostgresIdentityAgentDatabaseClient(IdentityAgentDatabaseClient):
    """PostgreSQL implementation of DatabaseClient"""
    
    def __init__(self):
        self.connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "identity_agent"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres")
        )
    
    def _execute(self, query: str, params: tuple = None):
        """Execute a query and return results"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def _execute_all(self, query: str, params: tuple = None) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def _row_to_registry_record(self, row: dict) -> AgentRegistryRecord:
        return AgentRegistryRecord(
            agent_id=row["agent_id"],
            tenant_id=row["tenant_id"],
            name=row["agent_id"],
            environment=row.get("environment"),
            type=None,
            purpose=None,
            role=row.get("role"),
            status=row["status"],
            risk_tier=row.get("risk_tier"),
            autonomy_level=row.get("autonomy_level"),
            ownership_team=row.get("ownership_team"),
            governance_tags=row.get("governance_tags") or [],
            created_at=row.get("registered_at"),
            updated_at=row.get("updated_at")
        )
    
    def _fetch_by_status(self, agent_id: str, status: str) -> Optional[AgentRegistryRecord]:
        query = """
            SELECT agent_id, tenant_id, environment, ownership_team,
                   registered_at, updated_at, status, role, risk_tier,
                   autonomy_level, allowed_tools, capabilities, governance_tags
            FROM agents
            WHERE agent_id = %s AND status = %s
        """
        result = self._execute(query, (agent_id, status))
        return self._row_to_registry_record(result) if result else None

    def fetch_from_registry_active(self, agent_id: str) -> Optional[AgentRegistryRecord]:
        return self._fetch_by_status(agent_id, "active")
    
    def fetch_from_registry_suspended(self, agent_id: str) -> Optional[AgentRegistryRecord]:
        return self._fetch_by_status(agent_id, "suspended")
    
    def fetch_from_registry_disabled(self, agent_id: str) -> Optional[AgentRegistryRecord]:
        return self._fetch_by_status(agent_id, "disabled")
    
    def fetch_from_registry_pending(self, agent_id: str) -> Optional[AgentRegistryRecord]:
        return self._fetch_by_status(agent_id, "pending")
    
    def fetch_agent_security_metadata(self, agent_id: str) -> Optional[AgentSecurityMetadata]:
        query = """
            SELECT agent_id, role, risk_tier, autonomy_level,
                   allowed_tools, capabilities, governance_tags, updated_at
            FROM agents
            WHERE agent_id = %s AND status = 'active'
        """
        result = self._execute(query, (agent_id,))
        if result:
            return AgentSecurityMetadata(
                agent_id=result["agent_id"],
                name=result["agent_id"],
                role=result.get("role") or "",
                risk_tier=result.get("risk_tier") or "low",
                autonomy_level=result.get("autonomy_level") or "read_only",
                allowed_tools=result.get("allowed_tools") or [],
                capabilities=result.get("capabilities") or [],
                governance_tags=result.get("governance_tags") or [],
                updated_at=result.get("updated_at")
            )
        return None

    def write_audit_log(self, log_event) -> bool:
        return True

    def get_active_signing_key(self) -> Optional[SigningKey]:
        query = """
            SELECT kid, private_key_pem, public_key_pem, algorithm,
                   active, created_at, expires_at
            FROM signing_keys
            WHERE active = true AND (expires_at IS NULL OR expires_at > NOW())
            ORDER BY created_at DESC
            LIMIT 1
        """
        row = self._execute(query)
        if row:
            return SigningKey(
                kid=row["kid"],
                private_key_pem=row["private_key_pem"],
                public_key_pem=row["public_key_pem"],
                algorithm=row["algorithm"],
                active=row["active"],
                created_at=row["created_at"],
                expires_at=row["expires_at"]
            )
        return None

    def get_signing_key_by_kid(self, kid: str) -> Optional[SigningKey]:
        query = """
            SELECT kid, private_key_pem, public_key_pem, algorithm,
                   active, created_at, expires_at
            FROM signing_keys
            WHERE kid = %s
        """
        row = self._execute(query, (kid,))
        if row:
            return SigningKey(
                kid=row["kid"],
                private_key_pem=row["private_key_pem"],
                public_key_pem=row["public_key_pem"],
                algorithm=row["algorithm"],
                active=row["active"],
                created_at=row["created_at"],
                expires_at=row["expires_at"]
            )
        return None

    def insert_signing_key(self, key: SigningKey) -> bool:
        query = """
            INSERT INTO signing_keys (kid, private_key_pem, public_key_pem, algorithm, active, created_at, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (
                    key.kid, key.private_key_pem, key.public_key_pem,
                    key.algorithm, key.active, key.created_at, key.expires_at
                ))
                self.connection.commit()
                return True
        except Exception:
            self.connection.rollback()
            raise

    def list_active_signing_keys(self) -> List[SigningKey]:
        query = """
            SELECT kid, private_key_pem, public_key_pem, algorithm,
                   active, created_at, expires_at
            FROM signing_keys
            WHERE active = true AND (expires_at IS NULL OR expires_at > NOW())
            ORDER BY created_at DESC
        """
        rows = self._execute_all(query)
        return [
            SigningKey(
                kid=r["kid"],
                private_key_pem=r["private_key_pem"],
                public_key_pem=r["public_key_pem"],
                algorithm=r["algorithm"],
                active=r["active"],
                created_at=r["created_at"],
                expires_at=r["expires_at"]
            )
            for r in rows
        ]

    def close(self):
        """Close the database connection"""
        self.connection.close()
