# Policy Engine Module

This is a beginner-friendly Node.js + Express backend for a Policy Decision Point (PDP) used in an Agentic Cybersecurity Platform.

## Project Structure

```text
.
|-- package.json
|-- server.js
|-- src
|   |-- controllers
|   |   `-- policyController.js
|   |-- policies
|   |   `-- policies.json
|   |-- routes
|   |   `-- toolCheckRoutes.js
|   |-- services
|   |   `-- policyService.js
|   `-- utils
|       `-- conditionMatcher.js
```

## Install

```bash
npm install
```

## Run

```bash
npm start
```

Server starts on `http://localhost:3000`.

## API

### POST `/check_tool_call`

Sample request:

```json
{
  "agent": {
    "agent_id": "triage-agent",
    "role": "SOC_AGENT",
    "risk_tier": "tier2",
    "autonomy_level": "medium",
    "allowed_tools": ["siem_query", "threat_intel"],
    "session_id": "SESSION-1001",
    "environment": "production"
  },
  "request": {
    "action": "run_tool",
    "tool": "siem_query",
    "data_sensitivity": "internal",
    "risk_score": 4
  }
}
```

Sample curl:

```bash
curl -X POST http://localhost:3000/check_tool_call \
  -H "Content-Type: application/json" \
  -d '{
    "agent": {
      "agent_id": "triage-agent",
      "role": "SOC_AGENT",
      "risk_tier": "tier2",
      "autonomy_level": "medium",
      "allowed_tools": ["siem_query", "threat_intel"],
      "session_id": "SESSION-1001",
      "environment": "production"
    },
    "request": {
      "action": "run_tool",
      "tool": "siem_query",
      "data_sensitivity": "internal",
      "risk_score": 4
    }
  }'
```

Sample response:

```json
{
  "decision": "ALLOW",
  "policy_id": "POLICY-004",
  "reason": "Tool is allowed and the request risk score is within the safe threshold"
}
```
