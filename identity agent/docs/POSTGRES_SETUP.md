# PostgreSQL Registry Setup

The identity agent can read registry records from PostgreSQL.

## 1. Install Python dependency

From the `identity agent/` folder:

```powershell
pip install -r requirements.txt
```

## 2. Set environment variables

Set these before running the driver:

```powershell
$env:IDENTITY_REGISTRY_BACKEND="postgres"
$env:POSTGRES_DSN="dbname=agentic_security user=postgres password=postgres host=localhost port=5432"
$env:POSTGRES_TABLE="agent_registry"
```

If PostgreSQL is unavailable, the code falls back to the in-memory registry so development can continue.

## 3. Create the schema

Run the SQL in [seed_registry.sql](/c:/Users/SAKETH/Documents/Project/Agentic%200T/identity%20agent/db/seed_registry.sql).

It creates the `agent_registry` table with the fields currently used by the identity service:

```sql
CREATE TABLE IF NOT EXISTS agent_registry (
  agent_id TEXT PRIMARY KEY,
  role TEXT NOT NULL,
  risk_tier TEXT NOT NULL,
  autonomy_level TEXT NOT NULL,
  capabilities TEXT[] NOT NULL,
  allowed_tools TEXT[] NOT NULL,
  status TEXT NOT NULL,
  owner TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  origin TEXT NOT NULL,
  network_zone TEXT NOT NULL
);
```

## 4. Seed sample agents

The SQL file also inserts:

- `triage-agent`
- `containment-agent`
- `blocked-agent`

## 5. Run the simulator

```powershell
python .\src\driver.py
```

Expected outcome:

- `triage-agent` resolves successfully
- `blocked-agent` is denied as suspended
- `ghost-agent` is denied as unknown
