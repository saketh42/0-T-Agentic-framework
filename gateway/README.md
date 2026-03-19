# Gateway Service

## Purpose

This service is the backend entrypoint for gateway checks described in `main.md`.

Current scope:

- health endpoint
- `/check_identity`
- `/check_plan`
- `/check_tool_call`
- `/check_io`

Right now the gateway is wired to the identity service first. Policy, DLP, and audit will be added next.

## Run

From the project root:

```powershell
uvicorn gateway.src.main:app --reload
```
