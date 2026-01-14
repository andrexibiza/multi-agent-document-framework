"""
Unit tests for Coordinator class.
"""

import pytest
import asyncio
from multi_agent_framework import (
    Agent,
    Coordinator,
    Config,
    WorkflowMode,
)


class TestCoordinator:
    """Test cases for Coordinator class."""
    
    def test_coordinator_initialization(self):
        """Test coordinator initialization."""
        agents = [
            Agent(role="researcher"),
            Agent(role="writer"),
        ]
        
        coordinator = Coordinator(agents=agents)
        
        assert len(coordinator.agents) == 2
        assert coordinator.workflow_mode == WorkflowMode.SEQUENTIAL
        assert coordinator.max_iterations == 3
    
    def test_coordinator_with_config(self):
        """Test coordinator with custom configuration."""
        agents = [Agent(role="writer")]
        config = Config()
        config.coordinator.max_iterations = 5
        
        coordinator = Coordinator(
            agents=agents,
            config=config,
        )
        
        assert coordinator.max_iterations == 5
    
    def test_workflow_mode_setting(self):
        """Test setting different workflow modes."""
        agents = [Agent(role="writer")]
        
        for mode in WorkflowMode:
            coordinator = Coordinator(
                agents=agents,
                workflow_mode=mode,
            )
            assert coordinator.workflow_mode == mode
    
    @pytest.mark.asyncio
    async def test_create_document_async(self):
        """Test asynchronous document creation."""
        agents = [
            Agent(role="researcher"),
            Agent(role="writer"),
        ]
        
        coordinator = Coordinator(agents=agents)
        
        document = await coordinator.create_document_async(
            topic="Test Document",
            requirements={"length": "500 words"},
        )
        
        assert document is not None
        assert document.title == "Test Document"
        assert document.status in ["draft", "final"]
    
    def test_create_document_sync(self):
        """Test synchronous document creation."""
        agents = [
            Agent(role="writer"),
        ]
        
        coordinator = Coordinator(agents=agents)
        
        document = coordinator.create_document(
            topic="Sync Test",
            requirements={},
        )
        
        assert document is not None
        assert document.title == "Sync Test"
    
    def test_get_workflow_status(self):
        """Test getting workflow status."""
        agents = [
            Agent(role="researcher"),
            Agent(role="writer"),
            Agent(role="editor"),
        ]
        
        coordinator = Coordinator(agents=agents)
        status = coordinator.get_workflow_status()
        
        assert "coordinator_id" in status
        assert "workflow_mode" in status
        assert "active_agents" in status
        assert status["active_agents"] == 3
    
    @pytest.mark.asyncio
    async def test_parallel_workflow(self):
        """Test parallel workflow execution."""
        agents = [
            Agent(role="writer"),
            Agent(role="writer"),
            Agent(role="writer"),
        ]
        
        coordinator = Coordinator(
            agents=agents,
            workflow_mode=WorkflowMode.PARALLEL,
        )
        
        document = await coordinator.create_document_async(
            topic="Parallel Test",
            requirements={},
        )
        
        assert document is not None


class TestWorkflowModes:
    """Test different workflow execution modes."""
    
    @pytest.mark.asyncio
    async def test_sequential_mode(self):
        """Test sequential workflow mode."""
        agents = [
            Agent(role="researcher"),
            Agent(role="writer"),
            Agent(role="editor"),
        ]
        
        coordinator = Coordinator(
            agents=agents,
            workflow_mode=WorkflowMode.SEQUENTIAL,
        )
        
        document = await coordinator.create_document_async(
            topic="Sequential Test",
            requirements={},
        )
        
        assert document is not None
    
    @pytest.mark.asyncio
    async def test_pipeline_mode(self):
        """Test pipeline workflow mode."""
        agents = [
            Agent(role="writer"),
            Agent(role="editor"),
        ]
        
        coordinator = Coordinator(
            agents=agents,
            workflow_mode=WorkflowMode.PIPELINE,
        )
        
        document = await coordinator.create_document_async(
            topic="Pipeline Test",
            requirements={},
        )
        
        assert document is not None