# Mongo Registry Setup

The identity agent can read registry records from MongoDB.

## Environment variables

Set these before running the driver:

```powershell
$env:IDENTITY_REGISTRY_BACKEND="mongo"
$env:MONGO_URI="mongodb://localhost:27017"
$env:MONGO_DB="agentic_security"
$env:MONGO_COLLECTION="agent_registry"
```

If MongoDB is unavailable, the code falls back to the in-memory registry so we can keep developing safely.

## Example document

```json
{
  "agent_id": "triage-agent",
  "role": "SOC_AGENT",
  "risk_tier": "tier2",
  "autonomy_level": "medium",
  "allowed_tools": ["siem_query", "threat_intel"],
  "status": "active",
  "owner": "SOC Platform"
}
```

## Next step

Once MongoDB is running, we should add a small seed script so the sample agents are inserted automatically.
