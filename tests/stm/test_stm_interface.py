"""
Unit tests for Agent Short-Term Memory interface and Redis client.

Tests the AgentShortTermMemoryClient abstract interface and RedisAgentShortTermMemoryClient implementation.
"""

import sys
import os
sys.path.insert(0, '../../src')

from stm import AgentShortTermMemoryClient
from stm_redis_client import RedisAgentShortTermMemoryClient
from schemas import AgentShortTermMemorySession
import pytest


class MockAgentShortTermMemoryClient(AgentShortTermMemoryClient):
    """Mock STM client for testing interface without Redis."""
    
    def __init__(self):
        self.sessions = {}
        self.ttl = 1800
    
    def create_session(self, session_id, agent_id, tenant_id, current_goal=""):
        session = AgentShortTermMemorySession(
            session_id=session_id,
            agent_id=agent_id,
            tenant_id=tenant_id,
            current_goal=current_goal,
            last_updated="2026-05-06 12:00:00"
        )
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id):
        return self.sessions.get(session_id)
    
    def update_plan(self, session_id, plan_step):
        session = self.sessions.get(session_id)
        if session:
            session.current_plan.append(plan_step)
            return session
        return None
    
    def add_intermediate_step(self, session_id, step_result):
        session = self.sessions.get(session_id)
        if session:
            session.intermediate_steps.append(step_result)
            return session
        return None
    
    def add_tool_output(self, session_id, tool_output):
        session = self.sessions.get(session_id)
        if session:
            session.recent_tool_outputs.append(tool_output)
            return session
        return None
    
    def update_flags(self, session_id, flags):
        session = self.sessions.get(session_id)
        if session:
            session.flags = flags
            return session
        return None
    
    def delete_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return "DENY"
    
    def extend_ttl(self, session_id):
        if session_id in self.sessions:
            return True
        return "DENY"


class TestAgentShortTermMemoryInterface:
    """Test AgentShortTermMemoryClient interface compliance."""
    
    def setup_method(self):
        self.stm = MockAgentShortTermMemoryClient()
    
    def test_create_session(self):
        """Test session creation."""
        session = self.stm.create_session("sess-1", "agent-1", "tenant-1", "Test goal")
        assert session is not None
        assert session.session_id == "sess-1"
        assert session.agent_id == "agent-1"
        assert session.tenant_id == "tenant-1"
        assert session.current_goal == "Test goal"
    
    def test_create_session_empty_goal(self):
        """Test session creation with empty goal."""
        session = self.stm.create_session("sess-2", "agent-2", "tenant-2")
        assert session.current_goal == ""
    
    def test_get_session_exists(self):
        """Test retrieving existing session."""
        self.stm.create_session("sess-3", "agent-3", "tenant-3")
        session = self.stm.get_session("sess-3")
        assert session is not None
        assert session.session_id == "sess-3"
    
    def test_get_session_not_exists(self):
        """Test retrieving non-existent session."""
        session = self.stm.get_session("non-existent")
        assert session is None
    
    def test_update_plan(self):
        """Test adding plan steps to session."""
        self.stm.create_session("sess-4", "agent-4", "tenant-4")
        session = self.stm.update_plan("sess-4", "Step 1: Investigate")
        assert "Step 1: Investigate" in session.current_plan
        
        session = self.stm.update_plan("sess-4", "Step 2: Analyze")
        assert len(session.current_plan) == 2
        assert "Step 2: Analyze" in session.current_plan
    
    def test_update_plan_no_session(self):
        """Test updating plan for non-existent session."""
        result = self.stm.update_plan("non-existent", "Step 1")
        assert result is None
    
    def test_add_intermediate_step(self):
        """Test adding intermediate steps."""
        self.stm.create_session("sess-5", "agent-5", "tenant-5")
        session = self.stm.add_intermediate_step("sess-5", "Found suspicious activity")
        assert "Found suspicious activity" in session.intermediate_steps
    
    def test_add_tool_output(self):
        """Test adding tool outputs."""
        self.stm.create_session("sess-6", "agent-6", "tenant-6")
        session = self.stm.add_tool_output("sess-6", "EDR scan results")
        assert "EDR scan results" in session.recent_tool_outputs
    
    def test_update_flags(self):
        """Test updating session flags."""
        self.stm.create_session("sess-7", "agent-7", "tenant-7")
        flags = {"priority": "high", "escalate": True}
        session = self.stm.update_flags("sess-7", flags)
        assert session.flags["priority"] == "high"
        assert session.flags["escalate"] == True
    
    def test_delete_session(self):
        """Test deleting a session."""
        self.stm.create_session("sess-8", "agent-8", "tenant-8")
        result = self.stm.delete_session("sess-8")
        assert result is True
        assert self.stm.get_session("sess-8") is None
    
    def test_delete_session_not_exists(self):
        """Test deleting non-existent session."""
        result = self.stm.delete_session("non-existent")
        assert result == "DENY"
    
    def test_extend_ttl(self):
        """Test extending TTL for existing session."""
        self.stm.create_session("sess-9", "agent-9", "tenant-9")
        result = self.stm.extend_ttl("sess-9")
        assert result is True
    
    def test_extend_ttl_not_exists(self):
        """Test extending TTL for non-existent session."""
        result = self.stm.extend_ttl("non-existent")
        assert result == "DENY"


@pytest.mark.skipif(not os.getenv("REDIS_HOST"), reason="Redis not available")
class TestRedisAgentShortTermMemoryClient:
    """Test RedisAgentShortTermMemoryClient implementation (requires Redis)."""
    
    def setup_method(self):
        self.stm = RedisAgentShortTermMemoryClient()
        self.test_session_id = "test-session-123"
    
    def teardown_method(self):
        """Clean up test session."""
        self.stm.delete_session(self.test_session_id)
    
    def test_create_and_get_session(self):
        """Test creating and retrieving session from Redis."""
        session = self.stm.create_session(
            self.test_session_id, "agent-redis", "tenant-redis", "Redis test"
        )
        assert session is not None
        assert session.session_id == self.test_session_id
        
        retrieved = self.stm.get_session(self.test_session_id)
        assert retrieved is not None
        assert retrieved.agent_id == "agent-redis"
    
    def test_update_plan_redis(self):
        """Test updating plan in Redis."""
        self.stm.create_session(self.test_session_id, "agent-1", "tenant-1")
        session = self.stm.update_plan(self.test_session_id, "Redis step 1")
        assert "Redis step 1" in session.current_plan
    
    def test_extend_ttl_redis(self):
        """Test extending TTL in Redis."""
        self.stm.create_session(self.test_session_id, "agent-1", "tenant-1")
        result = self.stm.extend_ttl(self.test_session_id)
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
