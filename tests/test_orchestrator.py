"""Tests for document orchestrator."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from madf import DocumentOrchestrator, DocumentRequest, OrchestratorConfig
from madf.models.document import DocumentStatus


@pytest.fixture
def config():
    """Create test configuration."""
    return OrchestratorConfig(
        max_agents=5,
        quality_threshold=0.80,
        timeout=60
    )


@pytest.fixture
def orchestrator(config):
    """Create orchestrator instance."""
    return DocumentOrchestrator(config)


@pytest.fixture
def sample_request():
    """Create sample document request."""
    return DocumentRequest(
        topic="Test Document",
        document_type="article",
        target_length=1000,
        style="formal",
        audience="general"
    )


class TestDocumentOrchestrator:
    """Test DocumentOrchestrator class."""
    
    def test_initialization(self, config):
        """Test orchestrator initialization."""
        orchestrator = DocumentOrchestrator(config)
        
        assert orchestrator.config == config
        assert len(orchestrator.agents) == 4
        assert 'research' in orchestrator.agents
        assert 'writing' in orchestrator.agents
        assert 'editing' in orchestrator.agents
        assert 'verification' in orchestrator.agents
    
    @pytest.mark.asyncio
    async def test_create_document_validation(self, orchestrator):
        """Test document request validation."""
        invalid_request = DocumentRequest(
            topic="Ab",  # Too short
            document_type="article",
            target_length=50  # Too short
        )
        
        with pytest.raises(ValueError):
            await orchestrator.create_document(invalid_request)
    
    @pytest.mark.asyncio
    @patch('madf.agents.research.ResearchAgent.execute')
    @patch('madf.agents.writing.WritingAgent.execute')
    @patch('madf.agents.editing.EditingAgent.execute')
    @patch('madf.agents.verification.VerificationAgent.execute')
    async def test_create_document_success(self,
                                          mock_verification,
                                          mock_editing,
                                          mock_writing,
                                          mock_research,
                                          orchestrator,
                                          sample_request):
        """Test successful document creation."""
        # Mock agent responses
        from madf.models.task import TaskResult
        
        mock_research.return_value = TaskResult(
            task_id="1",
            success=True,
            data={'research_brief': {'synthesis': 'test research'}}
        )
        
        mock_writing.return_value = TaskResult(
            task_id="2",
            success=True,
            data={'sections': [{'section_title': 'Test', 'content': 'test content'}]}
        )
        
        mock_editing.return_value = TaskResult(
            task_id="3",
            success=True,
            data={'edited_content': 'edited test content'}
        )
        
        mock_verification.return_value = TaskResult(
            task_id="4",
            success=True,
            data={
                'verification_report': {'overall_score': 0.90},
                'passed': True
            }
        )
        
        # Create document
        document = await orchestrator.create_document(sample_request)
        
        # Assertions
        assert document is not None
        assert document.status == DocumentStatus.COMPLETE
        assert document.quality_score == 0.90
        assert len(document.sections) > 0
    
    @pytest.mark.asyncio
    async def test_get_agent_metrics(self, orchestrator):
        """Test retrieving agent metrics."""
        metrics = orchestrator.get_agent_metrics()
        
        assert isinstance(metrics, dict)
        assert len(metrics) == 4
        assert all(k in metrics for k in ['research', 'writing', 'editing', 'verification'])


class TestOrchestratorConfig:
    """Test OrchestratorConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = OrchestratorConfig()
        
        assert config.max_agents == 10
        assert config.timeout == 300
        assert config.quality_threshold == 0.85
        assert config.enable_parallel is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = OrchestratorConfig(
            max_agents=20,
            quality_threshold=0.90
        )
        
        assert config.max_agents == 20
        assert config.quality_threshold == 0.90
    
    def test_config_to_dict(self):
        """Test config serialization."""
        config = OrchestratorConfig()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'orchestrator' in config_dict
        assert 'agents' in config_dict