"""
Agent Short-Term Memory (STM) client interface for Agentic Framework

Follows the same pattern as database.py for abstract interface.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from schemas import AgentShortTermMemorySession


class AgentShortTermMemoryClient(ABC):
    """
    Abstract interface for Agent Short-Term Memory operations.
    
    STM is per-session, Redis-backed with TTL (30 min default).
    Used for live agent reasoning: current plan, intermediate steps, tool outputs.
    """

    @abstractmethod
    def create_session(
        self,
        session_id: str,
        agent_id: str,
        tenant_id: str,
        current_goal: str = ""
    ) -> Optional[AgentShortTermMemorySession]:
        """Create a new STM session with default empty state."""
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[AgentShortTermMemorySession]:
        """Retrieve an existing STM session by session_id."""
        pass

    @abstractmethod
    def update_plan(self, session_id: str, plan_step: str) -> Optional[AgentShortTermMemorySession]:
        """Append a step to the current plan in STM."""
        pass

    @abstractmethod
    def add_intermediate_step(self, session_id: str, step_result: str) -> Optional[AgentShortTermMemorySession]:
        """Append an intermediate step result to STM."""
        pass

    @abstractmethod
    def add_tool_output(self, session_id: str, tool_output: str) -> Optional[AgentShortTermMemorySession]:
        """Append a tool output to STM."""
        pass

    @abstractmethod
    def update_flags(self, session_id: str, flags: Dict[str, Any]) -> Optional[AgentShortTermMemorySession]:
        """Update flags in STM session."""
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> bool | str:
        """Delete an STM session from Redis. Returns True on success, 'DENY' if session doesn't exist."""
        pass

    @abstractmethod
    def extend_ttl(self, session_id: str) -> bool | str:
        """Extend TTL for an existing STM session. Returns True on success, 'DENY' if session doesn't exist."""
        pass
