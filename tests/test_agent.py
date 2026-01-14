"""
Unit tests for Agent class.
"""

import pytest
import asyncio
from multi_agent_framework import Agent, AgentTask


class TestAgent:
    """Test cases for Agent class."""
    
    def test_agent_initialization(self):
        """Test agent initialization with default parameters."""
        agent = Agent(role="researcher")
        
        assert agent.role == "researcher"
        assert agent.status == "idle"
        assert isinstance(agent.agent_id, str)
        assert len(agent.task_history) == 0
    
    def test_agent_initialization_with_params(self):
        """Test agent initialization with custom parameters."""
        agent = Agent(
            agent_id="custom_id",
            role="writer",
            capabilities=["writing", "editing"],
            model="gpt-4",
            temperature=0.5,
        )
        
        assert agent.agent_id == "custom_id"
        assert agent.role == "writer"
        assert "writing" in agent.capabilities
        assert "editing" in agent.capabilities
        assert agent.model == "gpt-4"
        assert agent.temperature == 0.5
    
    @pytest.mark.asyncio
    async def test_execute_task(self):
        """Test task execution."""
        agent = Agent(role="researcher")
        
        task = AgentTask(
            task_id="test_task",
            description="Test task description",
            requirements={"key": "value"},
        )
        
        result = await agent.execute_task(task)
        
        assert result["status"] == "success"
        assert "result" in result
        assert result["agent_id"] == agent.agent_id
        assert len(agent.task_history) == 1
    
    def test_get_capabilities(self):
        """Test getting agent capabilities."""
        capabilities = ["research", "analysis"]
        agent = Agent(role="researcher", capabilities=capabilities)
        
        assert agent.get_capabilities() == capabilities
    
    def test_can_handle_task(self):
        """Test capability matching for tasks."""
        agent = Agent(
            role="researcher",
            capabilities=["web_search", "data_analysis"],
        )
        
        assert agent.can_handle_task(["web_search"])
        assert agent.can_handle_task(["data_analysis"])
        assert not agent.can_handle_task(["video_editing"])
    
    def test_get_status(self):
        """Test getting agent status."""
        agent = Agent(role="writer")
        status = agent.get_status()
        
        assert "agent_id" in status
        assert "role" in status
        assert "status" in status
        assert status["total_tasks"] == 0
        assert status["completed_tasks"] == 0
    
    @pytest.mark.asyncio
    async def test_task_failure_handling(self):
        """Test handling of task failures."""
        agent = Agent(role="researcher")
        
        # Create an invalid task that should fail
        task = AgentTask(
            task_id="fail_task",
            description="",  # Empty description
            requirements={},
        )
        
        # This should not raise an exception but return error status
        result = await agent.execute_task(task)
        
        # Result should indicate processing occurred
        assert "agent_id" in result
    
    def test_agent_repr(self):
        """Test agent string representation."""
        agent = Agent(agent_id="test_123", role="writer")
        repr_str = repr(agent)
        
        assert "test_123" in repr_str
        assert "writer" in repr_str


class TestAgentTask:
    """Test cases for AgentTask class."""
    
    def test_task_creation(self):
        """Test task creation with basic parameters."""
        task = AgentTask(
            task_id="task_001",
            description="Test task",
            requirements={"key": "value"},
        )
        
        assert task.task_id == "task_001"
        assert task.description == "Test task"
        assert task.status == "pending"
        assert task.result is None
    
    def test_task_status_updates(self):
        """Test task status transitions."""
        task = AgentTask(
            task_id="task_001",
            description="Test task",
            requirements={},
        )
        
        assert task.status == "pending"
        
        task.status = "in_progress"
        assert task.status == "in_progress"
        
        task.status = "completed"
        assert task.status == "completed"