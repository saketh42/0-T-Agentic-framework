# registry.py

import os

try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None


AGENT_REGISTRY = {
    "triage-agent": {
        "agent_id": "triage-agent",
        "role": "SOC_AGENT",
        "risk_tier": "tier2",
        "autonomy_level": "medium",
        "allowed_tools": ["siem_query", "threat_intel"],
        "status": "active",
        "owner": "SOC Platform"
    },
    "containment-agent": {
        "agent_id": "containment-agent",
        "role": "IR_AGENT",
        "risk_tier": "tier3",
        "autonomy_level": "high",
        "allowed_tools": ["isolate_host"],
        "status": "active",
        "owner": "IR Team"
    },
    "blocked-agent": {
        "agent_id": "blocked-agent",
        "role": "SOC_AGENT",
        "risk_tier": "tier2",
        "autonomy_level": "medium",
        "allowed_tools": ["siem_query"],
        "status": "suspended",
        "owner": "SOC Platform"
    }
}


class InMemoryRegistryRepository:
    def __init__(self, registry_data):
        self.registry_data = registry_data

    def get_agent(self, agent_id):
        return self.registry_data.get(agent_id)


class MongoRegistryRepository:
    def __init__(self, connection_string, database_name, collection_name):
        self.connection_string = connection_string
        self.database_name = database_name
        self.collection_name = collection_name

    def get_agent(self, agent_id):
        if MongoClient is None:
            raise RuntimeError("PYMONGO_NOT_INSTALLED")

        client = MongoClient(self.connection_string, serverSelectionTimeoutMS=2000)
        try:
            collection = client[self.database_name][self.collection_name]
            return collection.find_one({"agent_id": agent_id}, {"_id": 0})
        finally:
            client.close()


def _build_repository():
    use_mongo = os.getenv("IDENTITY_REGISTRY_BACKEND", "memory").lower() == "mongo"

    if not use_mongo:
        print("[Registry] Using in-memory registry backend")
        return InMemoryRegistryRepository(AGENT_REGISTRY)

    connection_string = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    database_name = os.getenv("MONGO_DB", "agentic_security")
    collection_name = os.getenv("MONGO_COLLECTION", "agent_registry")

    print("[Registry] Using MongoDB registry backend")
    return MongoRegistryRepository(connection_string, database_name, collection_name)


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
