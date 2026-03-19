# registry.py

import os

try:
    import psycopg
except ImportError:
    psycopg = None


AGENT_REGISTRY = {
    "triage-agent": {
        "agent_id": "triage-agent",
        "role": "SOC_AGENT",
        "risk_tier": "tier2",
        "autonomy_level": "medium",
        "capabilities": ["investigation", "triage"],
        "allowed_tools": ["siem_query", "threat_intel"],
        "status": "active",
        "owner": "SOC Platform",
        "tenant_id": "tenant-acme",
        "origin": "soc-copilot-ui",
        "network_zone": "internal"
    },
    "containment-agent": {
        "agent_id": "containment-agent",
        "role": "IR_AGENT",
        "risk_tier": "tier3",
        "autonomy_level": "high",
        "capabilities": ["containment", "response"],
        "allowed_tools": ["isolate_host"],
        "status": "active",
        "owner": "IR Team",
        "tenant_id": "tenant-acme",
        "origin": "ir-console",
        "network_zone": "internal"
    },
    "blocked-agent": {
        "agent_id": "blocked-agent",
        "role": "SOC_AGENT",
        "risk_tier": "tier2",
        "autonomy_level": "medium",
        "capabilities": ["investigation"],
        "allowed_tools": ["siem_query"],
        "status": "suspended",
        "owner": "SOC Platform",
        "tenant_id": "tenant-acme",
        "origin": "soc-copilot-ui",
        "network_zone": "restricted"
    }
}


class InMemoryRegistryRepository:
    def __init__(self, registry_data):
        self.registry_data = registry_data

    def get_agent(self, agent_id):
        return self.registry_data.get(agent_id)


class PostgresRegistryRepository:
    def __init__(self, connection_string, table_name):
        self.connection_string = connection_string
        self.table_name = table_name

    def get_agent(self, agent_id):
        if psycopg is None:
            raise RuntimeError("PSYCOPG_NOT_INSTALLED")

        query = f"""
            SELECT
                agent_id,
                role,
                risk_tier,
                autonomy_level,
                capabilities,
                allowed_tools,
                status,
                owner,
                tenant_id,
                origin,
                network_zone
            FROM {self.table_name}
            WHERE agent_id = %s
        """

        with psycopg.connect(self.connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (agent_id,))
                row = cursor.fetchone()

        if not row:
            return None

        return {
            "agent_id": row[0],
            "role": row[1],
            "risk_tier": row[2],
            "autonomy_level": row[3],
            "capabilities": row[4],
            "allowed_tools": row[5],
            "status": row[6],
            "owner": row[7],
            "tenant_id": row[8],
            "origin": row[9],
            "network_zone": row[10]
        }


def _build_repository():
    use_postgres = os.getenv("IDENTITY_REGISTRY_BACKEND", "memory").lower() == "postgres"

    if not use_postgres:
        print("[Registry] Using in-memory registry backend")
        return InMemoryRegistryRepository(AGENT_REGISTRY)

    connection_string = os.getenv(
        "POSTGRES_DSN",
        "dbname=agentic_security user=postgres password=postgres host=localhost port=5432"
    )
    table_name = os.getenv("POSTGRES_TABLE", "agent_registry")

    print("[Registry] Using PostgreSQL registry backend")
    return PostgresRegistryRepository(connection_string, table_name)


def get_agent(agent_id):
    print("[Registry] Searching for agent:", agent_id)

    repository = _build_repository()

    try:
        agent = repository.get_agent(agent_id)
    except Exception as error:
        print("[Registry] Registry lookup failed:", error)
        print("[Registry] Falling back to in-memory registry")
        agent = InMemoryRegistryRepository(AGENT_REGISTRY).get_agent(agent_id)

    if agent:
        print("[Registry] Agent found in registry")
    else:
        print("[Registry] Agent NOT found")

    return agent
