"""Tests for coordination layer."""

import pytest
import asyncio

from madf.coordination import WorkflowManager, WorkflowBuilder, MessageBus, MessageType, Message
from madf.models.request import DocumentRequest


class TestWorkflowManager:
    """Test WorkflowManager class."""
    
    @pytest.fixture
    def workflow_manager(self):
        """Create workflow manager instance."""
        return WorkflowManager()
    
    def test_initialization(self, workflow_manager):
        """Test workflow manager initialization."""
        assert len(workflow_manager.workflows) > 0
        assert 'article' in workflow_manager.workflows
        assert 'paper' in workflow_manager.workflows
    
    def test_create_workflow_for_request(self, workflow_manager):
        """Test workflow creation from request."""
        request = DocumentRequest(
            topic="Test",
            document_type="article",
            target_length=1000
        )
        
        workflow = workflow_manager.create_workflow(request)
        
        assert workflow is not None
        assert len(workflow.stages) > 0
        assert workflow.stages[0].name == "research"


class TestWorkflowBuilder:
    """Test WorkflowBuilder class."""
    
    def test_builder_pattern(self):
        """Test workflow builder pattern."""
        workflow = (WorkflowBuilder("test")
            .add_stage("stage1", "research")
            .add_stage("stage2", "writing", depends_on=["stage1"])
            .build())
        
        assert workflow.name == "test"
        assert len(workflow.stages) == 2
        assert workflow.stages[1].depends_on == ["stage1"]
    
    def test_metadata(self):
        """Test setting workflow metadata."""
        workflow = (WorkflowBuilder("test")
            .add_stage("stage1", "research")
            .set_metadata("key", "value")
            .build())
        
        assert workflow.metadata["key"] == "value"


class TestMessageBus:
    """Test MessageBus class."""
    
    @pytest.fixture
    def message_bus(self):
        """Create message bus instance."""
        return MessageBus()
    
    @pytest.mark.asyncio
    async def test_publish_subscribe(self, message_bus):
        """Test message publish/subscribe."""
        received_messages = []
        
        async def handler(message):
            received_messages.append(message)
        
        # Subscribe
        message_bus.subscribe(MessageType.TASK_COMPLETE, handler)
        
        # Start bus
        await message_bus.start()
        
        # Publish message
        await message_bus.publish(Message(
            type=MessageType.TASK_COMPLETE,
            data={'test': 'data'}
        ))
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        # Stop bus
        await message_bus.stop()
        
        # Check message received
        assert len(received_messages) == 1
        assert received_messages[0].data['test'] == 'data'
    
    def test_get_stats(self, message_bus):
        """Test getting message bus statistics."""
        stats = message_bus.get_stats()
        
        assert isinstance(stats, dict)
        assert 'running' in stats
        assert 'queue_size' in stats