
---

# Agentic Cyber Security Platform Architecture

*(Zero Trust Gateway, Gateway, Memory Spine, HIL, and Personas)*

---

# 1. Purpose and Scope

This document defines the end to end architecture for an agentic cyber security platform that uses a Security & Privacy Gateway, Gateway, and a shared memory & knowledge spine to secure multi agent workflows. The scope includes:

• Human personas (SOC, IR, governance, engineering).
• Agent libraries and orchestrator.
• Human in the loop (HIL) tools.
• Identity, policy, DLP and audit components.
• Memory layers (STM/MTM/LTM), Security Knowledge Graph, and Security Digital Twin.
• External tools and data sources.
• Alignment with zero trust and agentic governance principles.

---

# 2. Personas and Responsibilities

## 2.1 Core personas

• **SOC Analyst / Threat Hunter (SA)**
• Uses SOC Co pilot, case/incident views, and memory browser.
• Initiates investigations and hunts; reviews agent suggestions; approves low/medium impact actions.

• **Incident Responder / IR Lead (IR)**
• Uses case views, twin simulation, and approvals console.
• Owns high impact actions (containment, eradication); coordinates complex incidents.

• **Governance / Compliance Officer (GOV)**
• Uses policy dashboards, policy/runbook editor, and audit/logchain views.
• Defines and reviews policies, guardrails, and compliance controls; approves high impact policy changes.

• **AI Engineering / Platform Owner (ENG)**
• Owns agent libraries, orchestrator, Security & Privacy Gateway, memory APIs, KG and Twin services.
• Ensures reliability, performance, safety, and adherence to zero trust and agentic governance frameworks.

---

## 2.2 RACI summary (high level)

• **HIL tools & UIs:**
• SA/IR are Responsible for daily use; GOV is Accountable/Consulted for policy linked tooling; ENG is Accountable for implementation.

• **Agent libraries & orchestrator:**
• ENG is Responsible and Accountable; SA/IR/GOV are Consulted/Informed.

• **Gateway & Policy/DLP/Audit:**
• ENG and GOV share ownership (ENG: implementation; GOV: policy content and governance).

• **Memory & knowledge layers:**
• ENG is Accountable for infrastructure; SA/IR use MTM/LTM/KG/Twin; GOV oversees retention and compliance.

---

# 3. Layered Architecture Overview

From top to bottom, the system is structured into five layers:

1. Interaction & Orchestration Layer
2. Security & Privacy Gateway Layer
3. Agentic Memory & Knowledge Layer
4. Tooling & Data Source Layer
5. Platform & Infrastructure Layer

---

## 3.1 Logical architecture diagram (text)

```
       ┌───────────────────────────────────────────────────────────┐
       │                          Personas                         │
       │  • SOC Analyst / Threat Hunter                            │
       │  • Incident Responder / IR Lead                           │
       │  • Governance / Compliance Officer                        │
       │  • AI Engineering / Platform Owner                        │
       └───────────────▲───────────────────────────────────────────┘
                       │ (UIs, dashboards, approvals, feedback)
                       ▼
       ┌───────────────────────────────────────────────────────────┐
       │              Human-in-the-Loop (HIL) Tools                │
       │  • SOC Co-pilot UI (chat + actions panel)                 │
       │  • Case / Incident view & Memory browser                  │
       │  • Policy & Runbook editor                                │
       │  • Approval & override console                            │
       │  • Twin simulation / what-if views                        │
       └───────────────▲───────────────────────────────────────────┘
                       │ (requests, approvals, feedback signals)
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│           Agentic Orchestration & Agent Libraries                   │
│                                                                     │
│  Agent Libraries & Runtime:                                         │
│    • LLM agent framework / SDK (planning, tools, memory adapters)   │
│    • Gateway Client SDK (policy, identity, DLP, audit)              │
│                                                                     │
│  Core Agents:                                                       │
│    • Planner Agent                                                  │
│    • Triage Agent                                                   │
│    • Enrichment Agent                                               │
│    • Containment Agent                                              │
│    • Governance / Advisory Agents                                   │
│                                                                     │
│  Agents call:                                                       │
│    • Tool Adapters (SIEM, EDR, IAM, ticketing, cloud, etc.)         │
│    • Memory Adapters (STM/MTM/LTM, KG, Twin)                        │
│    • Gateway Client SDK (for every plan/tool/IO/memory call)        │
└──────────────────────▲──────────────────────────────────────────────┘
                       │ (mTLS/GRPC/HTTP via SDK)
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Security & Privacy Gateway                        │
│                                                                     │
│   • Identity & Context Service                                      │
│   • Gateway (ABAC + risk)                                      │
│   • Privacy / DLP Agent                                             │
│   • Audit Logchain & Metrics                                        │
│                                                                     │
│   Endpoints: /check_plan /check_tool_call /check_io /verify_log...  │
└───────────────┬─────────────────────────────────────────────────────┘
                │ (authorized, policy-enforced calls)
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 Agentic Memory & Knowledge Layer                    │
│                                                                     │
│  Short-Term Memory (STM)                                           │
│    • In-process + Redis per agent/session                          │
│                                                                     │
│  Medium-Term Memory (MTM)                                          │
│    • Dist. cache / doc store per incident/session                  │
│                                                                     │
│  Long-Term Memory (LTM)                                            │
│    • Vector DB, search index, doc store                            │
│                                                                     │
│  Security Knowledge Graph & Ontology                               │
│                                                                     │
│  Security Digital Twin                                             │
└──────────────────────▲──────────────────────────────────────────────┘
                       │ (mediated by Gateway & memory APIs)
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Tools & Data Source Layer                       │
│  • SIEM / Log platforms                                             │
│  • EDR/NDR/IDS                                                      │
│  • IAM / IDP / Directory                                            │
│  • CMDB / Asset inventory                                           │
│  • Cloud provider APIs                                              │
│  • Threat intel feeds                                               │
│  • Ticketing / ITSM                                                 │
│  • LLM / model endpoints                                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

# 4. Agent Libraries and Orchestration

## 4.1 Agent libraries

The agent library is the canonical runtime for all internal agents:

• Planning primitives
• ReAct style loops, tree of thought, or graph based planners for breaking goals into plans.

• Tool abstractions
• Typed client wrappers for SIEM, EDR, IAM, ticketing, cloud APIs, etc.
• All tool clients route through the Gateway Client SDK, never directly to external systems.

• Memory adapters
• stm_client, mtm_client, ltm_client, kg_client, twin_client.
• Automatically attach agent_id, tenant_id, and context for identity and policy evaluation.

• Gateway Client SDK
• Methods such as:

```
gateway.check_plan(plan, ctx)
gateway.check_tool_call(tool_call, ctx)
gateway.check_io(io_payload, ctx)
```

• Handles authentication, retries, and telemetry.

---

## 4.2 Orchestration pattern

Use a centralized orchestrator pattern with a Planner Agent coordinating worker agents (triage, enrichment, containment, governance):

• Planner Agent
• Interprets user goals and HIL inputs.
• Generates plans with explicit steps and tool/memory operations.
• Submits plans for /check_plan.

• Worker agents
• Execute plan steps, calling tools and memory via Gateway.
• Emit structured events for MTM and LTM.

This pattern keeps decision traces clear and enables zero trust checks at each step.

---

# 5. Human in the Loop (HIL) Tooling

## 5.1 SOC Co pilot UI

• Chat interface for SA/IR to express tasks in natural language.
• “Actions panel” showing suggested agent actions and reasoning.

• Allows:

• Approve/deny suggested steps or whole plans.
• Request additional context from memory (MTM/LTM/KG/Twin).

---

## 5.2 Case / Incident view and Memory browser

• Timeline of alerts, agent actions, tool calls, and human interventions for each incident.

• “Memory browser”:

• STM snapshot: what agents are currently “thinking” about.
• MTM: per incident trail of steps and hypotheses.
• LTM: past similar incidents and knowledge articles.
• KG & Twin: neighborhood of affected entities, paths, and current security posture.

---

## 5.3 Policy & Runbook editor

• No/low code interface for governance users to define and edit:

• Policy rules consumed by the Gateway.
• Runbooks used by Planner and worker agents.

• Integrated test harness:

• Apply candidate policies on stored scenarios before enabling (audit → enforce).

---

## 5.4 Approval & override console

• Shows all escalate decisions from Gateway (e.g., high risk actions or plans).

• IR/GOV can:

• Approve with justification.
• Deny and override with a safer alternative.

• All overrides are logged and fed back into governance metrics.

---

## 5.5 Twin simulation views

• Visual UI for simulating proposed containment actions in the Security Digital Twin before applying them in production.

• Used by IR and GOV to validate agent proposals.

---

# 6. Security & Privacy Gateway and Gateway

## 6.1 Identity & Context Service

• Implements non human identity for agents and services under zero trust.

• Responsibilities:

• Validate agent tokens (JWT/mTLS) with claims such as agent_id, role, autonomy_level, tenant_id.
• Resolve agent metadata from registry (owner, capabilities, risk tier).
• Attach context attributes to each DecisionContext: environment, network zone, session, origin.

---

## 6.2 Gateway

• ABAC style policy as code engine acting as Policy Decision Point (PDP):

• Inputs: DecisionContext (agent, tool, data, context, risk).

• Outputs: allow|deny|sanitize|escalate plus reasons, policy_ids, threat_tags, severity.

• Policy types include:

• Agent identity, role, autonomy constraints.
• Tool category and endpoint restrictions.
• Data classification and DLP driven decisions.
• Plan level risk, multi step behavior and separation of duties.
• Governance and logging requirements.

---

## 6.3 Privacy / DLP Agent

• Performs:

• Data classification (public/internal/secret/PII/credential).
• Masking/sanitization on inputs and outputs that cross trust boundaries.
• Checks before writing to LTM/KG/Twin or external tools.

• Outputs classification and recommended actions to Gateway as attributes.

---

## 6.4 Audit Logchain & Metrics

• Provides complete, tamper evident logging of agent activity.

• Logchain:

• Append only events for all Gateway decisions and key tool/memory operations.
• Hash chaining for tamper evidence and post incident forensics.

• Metrics:

• Policy hits, decisions, severities.
• DLP events.
• Latency, error rates, and per agent statistics.

---

# 7. Agentic Memory & Knowledge Layer

## 7.1 Short Term Memory (STM)

• Scope: per agent, per session working memory for live reasoning (prompt window, current alert, narrow log snippets, candidate hypotheses).

• Implementation:

• In process data structures plus low latency store (Redis) keyed by session_id or incident_id.

• Governance:

• Tight TTL and scope; optionally viewable via HIL tools when needed.

---

## 7.2 Medium Term Memory (MTM)

• Scope: per incident or per campaign session state:

• Sequence of steps, queries, enrichments, actions, and their results.
• Evolving hypotheses and decisions.

• Implementation:

• Distributed cache or document DB keyed by incident_id.

• Stores structured episodes plus embeddings for retrieval and summarization.

• Exposed as the incident timeline in HIL tools.

---

## 7.3 Long Term Memory (LTM)

• Scope: persistent security knowledge and history:

• Prior incidents, threat intelligence, runbooks, knowledge articles, training examples.

• Implementation:

• Vector DB for semantic search over text and incident summaries.
• Search index or SIEM like backend for time series and log style queries.
• Document store for artefacts and attachments.

• Governed by:

• Data classification and retention policies (no raw credentials, bounded PII, etc.).

• All writes pass through Gateway DLP and Gateway.

---

## 7.4 Security Knowledge Graph (SKG) & Ontology

• Graph of entities: users, identities, devices, hosts, IPs/domains, applications, alerts, incidents, controls, vulnerabilities.

• Ontology:

• Defines types, relationships, and integrity constraints.

• Supports reasoning (blast radius analysis, dependency paths, exposure queries).

---

## 7.5 Security Digital Twin

• Representational model of environment state:

• Network topology, access paths, identity relationships, control posture, exposures.

• Used for:

• Simulation of agent proposed actions.
• What if analysis by IR/GOV.

• Updated via connectors to SIEM, CMDB, cloud APIs, and IAM.

All memory and knowledge services are behind Memory APIs that are accessible only through the Gateway.

---

# 8. Tools & Data Source Layer

External systems that agents act upon or read from:

• Security telemetry: SIEM/log platforms, EDR/NDR/IDS.
• Identity and configuration: IAM/IDP/Directory, CMDB, asset inventory.
• Cloud and infrastructure: cloud provider APIs, Kubernetes/infra control planes.
• Case management: ticketing and ITSM systems.
• Threat intelligence: CTI feeds and platforms.
• Model endpoints: internal or external LLMs/foundation models used for reasoning and NLU.

All access to these systems is mediated by tool adapters that call the Gateway for every operation.

---

# 9. Data and Control Flows (End to End)

## 1. Goal initiation

• SA/IR or external client submits a goal via SOC Co pilot or API (for example, “Investigate alert A”).

---

## 2. Planning

• Planner Agent retrieves relevant context (alerts, prior incidents) via STM/MTM/LTM/KG/Twin.

• Generates a plan (sequence of steps with tool/memory operations).

• Plan is submitted to Gateway /check_plan for identity, policy, and risk evaluation.

---

## 3. Plan decision

• Identity & Context Service resolves agent identity and attributes.

• DLP classifies any data referenced in plan.

• Gateway evaluates plan level rules; may require human approval.

• Decision is logged to logchain; if escalate, appears in Approval console.

---

## 4. Execution

• Worker agents execute approved steps.

• For each tool call:

• Gateway /check_tool_call with DecisionContext.

• If allow or sanitize, tool adapter invokes target system.

• For memory operations:

• /check_io and memory APIs enforce classification and retention policies.

---

## 5. Human oversight

• HIL tools present reasoning, actions, and alternatives to SA/IR/GOV.

• High impact steps may be gated by explicit approvals.

---

## 6. Learning and governance

• MTM and LTM capture rich episodes for future retrieval.

• GOV and ENG review policy hit metrics, overrides, and near misses to refine policies and agents.

---

# 10. Zero Trust and Governance Alignment

The architecture operationalizes Zero Trust for AI agents by:

• Eliminating implicit trust: every agent action is authenticated, authorized, and logged.
• Treating agents as first class, non human identities with bounded autonomy.
• Applying centralized, policy as code controls at a Gateway that all traffic passes through.
• Enforcing least privilege and dynamic, context aware authorization using attributes and risk.
• Maintaining comprehensive observability and tamper evident logs for analysis and governance.

At the same time, it follows emerging agentic AI security and governance guidance: multi agent design patterns, layered guardrails, and human in the loop oversight for high impact decisions.


# Architecture
- Python
- React.js
- postgresql
- redis
- pinecone
- neo4j
- elastic search
- docker
- kubernetes
- kafka

---

# Identity Agent Team Split

## Scope

Our team owns the identity agent flow and the schemas/contracts needed by the database team.

The database team will handle storage, queries, and persistence based on the schemas we provide.

## End-to-End Flow

1. Validate request
2. Look up agent in registry
3. Check whether agent is active or blocked
4. Fetch metadata
5. Build decision context
6. Issue JWT (RS256, signed with key from signing_keys table)
7. Store context in STM (Redis, 1-hour TTL)
8. Submit decision context to Gateway
9. Return final output (ALLOW + JWT, or DENY/BLOCK + failure_reason)

*Note: Audit logging is handled by the Gateway Audit Logchain (see §6.4), not the Identity Agent.*

## Person 1 Ownership

Person 1 owns the input side of the identity agent.

- Request schema
- Step 1 validation logic
- Step 2 registry lookup flow
- Invalid request handling
- Unknown agent handling
- Registry contract/schema for DB team

## Person 2 Ownership

Person 2 owns the output and enrichment side of the identity agent.

- Metadata schema needed from DB team
- Step 3 metadata fetch flow
- Active/blocked decision handling
- Decision context/output schema
- Audit log schema
- Final success response structure

## Shared Deliverables

- Full identity agent pseudocode
- Final architecture approval draft
- Handoff document for DB team
- Final schema review before implementation

## Schemas To Hand Off To DB Team

### Registry Schema

- `agent_id`
- `tenant_id`
- `environment`
- `status`
- `ownership_team`
- `registered_at`
- `updated_at`

### Metadata Schema

- `agent_id`
- `role`
- `risk_tier`
- `autonomy_level`
- `allowed_tools`
- `capabilities`
- `governance_tags`
- `updated_at`

### Audit Log Schema

- `event_id`
- `timestamp`
- `agent_id`
- `session_id`
- `tenant_id`
- `environment`
- `origin`
- `network_zone`
- `event_type`
- `decision`
- `reason`
- `hash` or `tamper_proof_ref`
