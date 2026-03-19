# Prioritized Task List

This task list is based on:

- `main.md`
- the current `identity agent/` implementation

Note:
- I do not currently see `policyEngine/` in this workspace snapshot, so policy tasks below are based on the architecture in `main.md` and earlier discussed implementation goals.

## Priority 0: Finish the current identity slice

These are the most important because they complete the first real platform component.

- Add audit log events for:
  - active agent resolved
  - unknown agent denied
  - suspended agent denied
- Add tests for:
  - active agent
  - suspended agent
  - unknown agent
  - PostgreSQL lookup fallback
- Add `.gitignore` for Python cache files.

Completed in this phase:

- PostgreSQL seed script for sample agents
- structured identity decision output instead of plain exceptions
- Add audit log events for:
- Expand `DecisionContext` with:
  - `tenant_id`
  - `origin`
  - `network_zone`
  - `capabilities`
- verified PostgreSQL CLI, server readiness, SQL seed, and Python driver path end to end

Why this is first:
- It turns the current identity demo into a usable service foundation.

## Priority 1: Build the Gateway backbone

This is the next most important step because `main.md` centers the whole system around the gateway.

- Create a gateway service/module.
- Add endpoint or handler for `/check_plan`.
- Add endpoint or handler for `/check_tool_call`.
- Add endpoint or handler for `/check_io`.
- Route all agent actions through the gateway flow.
- Make gateway call:
  - identity service first
  - then policy evaluation
  - then audit logging

Why this is high priority:
- Without this, the architecture is still separate demos instead of one system.

## Priority 2: Complete the Policy Agent MVP

- Return richer policy responses:
  - `decision`
  - `reasons`
  - `policy_ids`
  - `severity`
  - `threat_tags`
- Normalize decisions to:
  - `allow`
  - `deny`
  - `sanitize`
  - `escalate`
- Add policy priority field.
- Add plan-level rule evaluation.
- Add rules for:
  - tool allowlist
  - role restrictions
  - autonomy restrictions
  - risk score thresholds
  - production environment controls

Why this matters:
- `main.md` expects ABAC + risk, not only basic tool checks.

## Priority 3: Add DLP / Privacy checks

- Create a small DLP module.
- Classify payloads as:
  - `public`
  - `internal`
  - `secret`
  - `pii`
  - `credential`
- Add sanitize behavior for restricted outputs.
- Feed DLP classification into policy decisions.
- Use DLP before memory writes and external output.

Why this matters:
- `main.md` explicitly includes a Privacy / DLP Agent in the gateway layer.

## Priority 4: Add Audit Logchain baseline

- Create one final audit logger at the end of the gateway flow.
- Log after the request finishes the full gateway path:
  - identity check
  - policy check
  - DLP check if used
  - final decision
- Write one final audit event per request.
- The audit record should contain:
  - timestamp
  - agent_id
  - session_id
  - request type
  - requested action
  - tool or plan id
  - identity result
  - policy result
  - DLP result if used
  - final decision
  - reason
  - policy ids
  - severity
- If the request fails early, like unknown or suspended agent, still write the final failure outcome before exit.
- Start with JSON append-only logs.
- Later add hash chaining for tamper evidence.
- Add basic metrics counters:
  - allow count
  - deny count
  - escalate count
  - sanitize count

Why this matters:
- Logging and traceability are core architecture requirements in `main.md`.
- Logging once at the end gives a full end-to-end record instead of fragmented partial logs.

## Priority 5: Add planner and execution flow

- Create a simple planner agent simulation.
- Planner should generate a plan with steps.
- Submit the plan to `/check_plan`.
- If approved, pass steps to worker execution.
- For each step, call `/check_tool_call`.
- Record execution results into memory/audit logs.

Why this matters:
- `main.md` describes a plan-first workflow, not only single tool checks.

## Priority 6: Add tool adapter stubs

- Create simple adapters for:
  - SIEM
  - EDR
  - IAM
  - ticketing
- Ensure adapters never execute directly without gateway approval.
- Add one mock action per adapter for simulation.

Why this matters:
- The architecture says all tool access must be mediated through the gateway.

## Priority 7: Add memory layer stubs

- Add STM stub:
  - per session working memory
- Add MTM stub:
  - per incident history
- Add LTM stub:
  - persistent knowledge store placeholder
- Add gateway protection for memory reads/writes.
- Store plan execution events in MTM.

Why this matters:
- Memory is a major layer in `main.md` and supports future agent workflows.

## Priority 8: Add HIL approval flow

- Create simple approval queue for escalated decisions.
- Allow human approve/deny input.
- Record overrides in audit logs.
- Show reason and policy metadata with escalation.

Why this matters:
- `main.md` expects human-in-the-loop approval for high-risk actions and plans.

## Priority 9: Improve project structure

- Separate services into clear folders:
  - `gateway/`
  - `identity-agent/`
  - `policy-agent/`
  - `dlp-agent/`
  - `audit/`
  - `memory/`
  - `agents/`
  - `adapters/`
- Add root-level setup instructions.
- Add `.env.example`.
- Add test folder and sample requests.

Why this matters:
- It will get messy quickly if the project grows without structure.

## Recommended build order

1. Identity hardening
2. Gateway shell
3. Policy MVP completion
4. Audit logging at gateway exit
5. DLP stub
6. Plan flow
7. Tool adapters
8. Memory stubs
9. HIL approvals
10. Cleanup and tests everywhere

## Suggested immediate next tasks

If we want the best short-term progress, do these next:

1. Create gateway backend with `/check_plan`, `/check_tool_call`, and `/check_io` entry points.
2. Wire gateway identity checks to the working PostgreSQL-backed identity service.
3. Upgrade policy response format to match `main.md`.
4. Add final audit logging at gateway exit.
5. Add tests for identity and gateway flows.
