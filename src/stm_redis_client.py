"""
Redis-based Agent Short-Term Memory client for Agentic Framework

Implements AgentShortTermMemoryClient interface using Redis for per-session agent memory.
Session expires after SESSION_TTL seconds (default 1800 = 30 minutes).
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime

import redis

from stm import AgentShortTermMemoryClient
from schemas import AgentShortTermMemorySession


class RedisAgentShortTermMemoryClient(AgentShortTermMemoryClient):
    """
    Redis implementation of AgentShortTermMemoryClient.
    
    Configuration via environment variables:
    - REDIS_HOST (default: localhost)
    - REDIS_PORT (default: 6379)
    - STM_TTL (default: 1800 seconds = 30 minutes)
    """

    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            decode_responses=True
        )
        self.session_ttl = int(os.getenv("STM_TTL", "1800"))

    def create_session(
        self,
        session_id: str,
        agent_id: str,
        tenant_id: str,
        current_goal: str = ""
    ) -> Optional[AgentShortTermMemorySession]:
        """Create a new STM session with default empty state."""
        stm_data = {
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

        self.redis_client.setex(
            session_id,
            self.session_ttl,
            json.dumps(stm_data)
        )
        return AgentShortTermMemorySession(**stm_data)

    def get_session(self, session_id: str) -> Optional[AgentShortTermMemorySession]:
        """Retrieve an existing STM session by session_id."""
        raw = self.redis_client.get(session_id)
        if raw:
            data = json.loads(raw)
            return AgentShortTermMemorySession(**data)
        return None

    def update_plan(self, session_id: str, plan_step: str) -> Optional[AgentShortTermMemorySession]:
        """Append a step to the current plan in STM."""
        return self._update_session_list(session_id, "current_plan", plan_step)

    def add_intermediate_step(self, session_id: str, step_result: str) -> Optional[AgentShortTermMemorySession]:
        """Append an intermediate step result to STM."""
        return self._update_session_list(session_id, "intermediate_steps", step_result)

    def add_tool_output(self, session_id: str, tool_output: str) -> Optional[AgentShortTermMemorySession]:
        """Append a tool output to STM."""
        return self._update_session_list(session_id, "recent_tool_outputs", tool_output)

    def update_flags(self, session_id: str, flags: Dict[str, Any]) -> Optional[AgentShortTermMemorySession]:
        """Update flags in STM session."""
        raw = self.redis_client.get(session_id)
        if raw:
            data = json.loads(raw)
            data["flags"] = flags
            data["last_updated"] = str(datetime.now())
            self.redis_client.setex(
                session_id,
                self.session_ttl,
                json.dumps(data)
            )
            return AgentShortTermMemorySession(**data)
        return None

    def delete_session(self, session_id: str) -> bool:
        """Delete an STM session from Redis."""
        return bool(self.redis_client.delete(session_id))

    def extend_ttl(self, session_id: str) -> bool:
        """Extend TTL for an existing STM session."""
        return bool(self.redis_client.expire(session_id, self.session_ttl))

    def _update_session_list(
        self,
        session_id: str,
        field: str,
        value: str
    ) -> Optional[AgentShortTermMemorySession]:
        """Helper to append to a list field in STM and update TTL."""
        raw = self.redis_client.get(session_id)
        if raw:
            data = json.loads(raw)
            data[field].append(value)
            data["last_updated"] = str(datetime.now())
            self.redis_client.setex(
                session_id,
                self.session_ttl,
                json.dumps(data)
            )
            return AgentShortTermMemorySession(**data)
        return None
