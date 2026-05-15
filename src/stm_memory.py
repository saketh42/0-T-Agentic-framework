"""In-memory STM client — fallback when Redis is unavailable."""

from typing import Optional, Dict, Any
from datetime import datetime
from stm import AgentShortTermMemoryClient
from schemas import AgentShortTermMemorySession, AgentIdentityDecisionContext


class MemoryAgentShortTermMemoryClient(AgentShortTermMemoryClient):
    def __init__(self):
        self._sessions: Dict[str, dict] = {}
        self._contexts: Dict[str, dict] = {}

    def create_session(self, session_id: str, agent_id: str, tenant_id: str, current_goal: str = ""):
        data = {
            "session_id": session_id,
            "agent_id": agent_id,
            "tenant_id": tenant_id,
            "current_goal": current_goal,
            "current_plan": [],
            "intermediate_steps": [],
            "recent_tool_outputs": [],
            "flags": {},
            "last_updated": str(datetime.now())
        }
        self._sessions[session_id] = data
        return AgentShortTermMemorySession(**data)

    def get_session(self, session_id: str):
        raw = self._sessions.get(session_id)
        return AgentShortTermMemorySession(**raw) if raw else None

    def store_decision_context(self, session_id: str, context: AgentIdentityDecisionContext) -> bool:
        self._contexts[session_id] = context.model_dump(mode="json")
        return True

    def get_decision_context(self, session_id: str):
        raw = self._contexts.get(session_id)
        return AgentIdentityDecisionContext(**raw) if raw else None

    def update_plan(self, session_id: str, plan_step: str):
        return self._update_field(session_id, "current_plan", plan_step)

    def add_intermediate_step(self, session_id: str, step_result: str):
        return self._update_field(session_id, "intermediate_steps", step_result)

    def add_tool_output(self, session_id: str, tool_output: str):
        return self._update_field(session_id, "recent_tool_outputs", tool_output)

    def update_flags(self, session_id: str, flags: Dict[str, Any]):
        raw = self._sessions.get(session_id)
        if raw:
            raw["flags"] = flags
            raw["last_updated"] = str(datetime.now())
            return AgentShortTermMemorySession(**raw)
        return None

    def delete_session(self, session_id: str) -> bool:
        return bool(self._sessions.pop(session_id, None))

    def extend_ttl(self, session_id: str) -> bool:
        return session_id in self._sessions

    def _update_field(self, session_id: str, field: str, value: str):
        raw = self._sessions.get(session_id)
        if raw:
            raw[field].append(value)
            raw["last_updated"] = str(datetime.now())
            return AgentShortTermMemorySession(**raw)
        return None
