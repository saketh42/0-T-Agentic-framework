"""
PostgreSQL Database Client for Identity Agent

Implements the DatabaseClient interface using psycopg2.
"""

import os
from typing import Optional, List
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

from schemas import AgentRegistryRecord, AgentSecurityMetadata, SigningKey
from database import IdentityAgentDatabaseClient


class PostgresIdentityAgentDatabaseClient(IdentityAgentDatabaseClient):
    """PostgreSQL implementation of DatabaseClient"""
    
    def __init__(self):
        load_dotenv()
        self.connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "identity_agent"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres")
        )
        self._ensure_tables()

    def _ensure_tables(self):
        with self.connection.cursor() as cur:
            cur.execute("""
                DROP TABLE IF EXISTS agents CASCADE;
                CREATE TABLE agents (
                    agent_id TEXT PRIMARY KEY,
                    tenant_id TEXT,
                    name VARCHAR(100) NOT NULL,
                    type VARCHAR(50),
                    purpose TEXT,
                    environment TEXT,
                    role VARCHAR(50),
                    status VARCHAR(20) NOT NULL DEFAULT 'active',
                    risk_tier VARCHAR(20) DEFAULT 'low',
                    autonomy_level INT CHECK (autonomy_level BETWEEN 1 AND 5),
                    allowed_tools TEXT[] DEFAULT '{}',
                    capabilities TEXT[] DEFAULT '{}',
                    governance_tags TEXT[] DEFAULT '{}',
                    ownership_team TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS signing_keys (
                    kid TEXT PRIMARY KEY,
                    private_key_pem TEXT NOT NULL,
                    public_key_pem TEXT NOT NULL,
                    algorithm TEXT NOT NULL DEFAULT 'RS256',
                    active BOOLEAN DEFAULT true,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    expires_at TIMESTAMPTZ
                );
            """)
            self._seed_demo_agents()
            self._seed_signing_key()
            self.connection.commit()

    def _seed_demo_agents(self):
        with self.connection.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM agents")
            if cur.fetchone()[0] > 0:
                return
        demo = [
            ("agent-001", "tenant-acme", "Agent-001", "automation", "Identity management", "prod", "developer", "active", "low", 5,
             ["read", "write", "execute"], ["code_review", "deploy"], ["pci", "hipaa"], "platform"),
            ("agent-002", "tenant-acme", "Agent-002", "monitoring", "Session watch", "staging", "developer", "suspended", "medium", 2,
             ["read"], ["code_review"], ["pci"], "platform"),
            ("agent-highrisk", "tenant-acme", "Agent-HighRisk", "admin", "System administration", "prod", "admin", "active", "critical", 5,
             ["read", "write", "execute", "admin"], ["deploy", "audit", "rollback"], ["pci", "hipaa", "sox"], "security"),
        ]
        with self.connection.cursor() as cur:
            cur.executemany("""
                INSERT INTO agents (agent_id, tenant_id, name, type, purpose, environment, role, status, risk_tier, autonomy_level, allowed_tools, capabilities, governance_tags, ownership_team)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (agent_id) DO NOTHING
            """, demo)

    def _seed_signing_key(self):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend
        from issue_jwt import _fingerprint

        with self.connection.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM signing_keys")
            if cur.fetchone()[0] > 0:
                return
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        kid = _fingerprint(public_pem)
        key = SigningKey(
            kid=kid, private_key_pem=private_pem, public_key_pem=public_pem,
            algorithm="RS256", active=True,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
        )
        self.insert_signing_key(key)

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
            tenant_id=row.get("tenant_id"),
            name=row.get("name") or row["agent_id"],
            environment=row.get("environment"),
            type=row.get("type"),
            purpose=row.get("purpose"),
            role=row.get("role"),
            status=row["status"],
            risk_tier=row.get("risk_tier"),
            autonomy_level=str(row["autonomy_level"]) if row.get("autonomy_level") is not None else None,
            ownership_team=row.get("ownership_team"),
            governance_tags=row.get("governance_tags") or [],
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at")
        )
    
    def _fetch_by_status(self, agent_id: str, status: str) -> Optional[AgentRegistryRecord]:
        query = """
            SELECT agent_id, tenant_id, name, type, purpose, environment,
                   ownership_team, created_at, updated_at, status, role, risk_tier,
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
            SELECT agent_id, name, role, risk_tier, autonomy_level,
                   allowed_tools, capabilities, governance_tags, updated_at
            FROM agents
            WHERE agent_id = %s AND status = 'active'
        """
        result = self._execute(query, (agent_id,))
        if result:
            return AgentSecurityMetadata(
                agent_id=result["agent_id"],
                name=result.get("name") or result["agent_id"],
                role=result.get("role") or "",
                risk_tier=result.get("risk_tier") or "low",
                autonomy_level=str(result["autonomy_level"]) if result.get("autonomy_level") is not None else "read_only",
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
        self._auto_generate_key()
        return self.get_active_signing_key()

    def _auto_generate_key(self):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend
        from issue_jwt import _fingerprint
        from datetime import datetime, timedelta, timezone

        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=2048, backend=default_backend()
            )
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode()
            public_pem = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
            kid = _fingerprint(public_pem)
            key = SigningKey(
                kid=kid, private_key_pem=private_pem, public_key_pem=public_pem,
                algorithm="RS256", active=True,
                created_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            )
            self.insert_signing_key(key)
        except Exception as e:
            print(f"Warning: could not auto-generate signing key: {e}")

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
