"""Tests for agent implementations."""

import pytest
from unittest.mock import AsyncMock, patch

from madf.agents import ResearchAgent, WritingAgent, EditingAgent, VerificationAgent
from madf.models.task import Task, TaskResult
from madf.utils.config import AgentConfig, ModelConfig


@pytest.fixture
def agent_config():
    """Create test agent configuration."""
    return AgentConfig(
        name="test_agent",
        model_config=ModelConfig(
            model="gpt-4",
            temperature=0.7
        ),
        timeout=60
    )


class TestResearchAgent:
    """Test ResearchAgent class."""
    
    @pytest.fixture
    def research_agent(self, agent_config):
        """Create research agent instance."""
        agent_config.name = "research"
        return ResearchAgent(agent_config)
    
    def test_initialization(self, research_agent):
        """Test research agent initialization."""
        assert research_agent.name == "research"
        assert research_agent.specialization == "research"
        assert research_agent.state == "idle"
    
    @pytest.mark.asyncio
    @patch('madf.utils.llm_client.LLMClient.generate')
    async def test_process_research_task(self, mock_generate, research_agent):
        """Test research task processing."""
        mock_generate.return_value = '["Question 1", "Question 2"]'
        
        task = Task(
            id="test_1",
            type="research",
            data={'query': 'Test topic', 'depth': 'shallow'}
        )
        
        result = await research_agent.process(task)
        
        assert result.success is True
        assert 'research_brief' in result.data
        assert 'sub_queries' in result.data


class TestWritingAgent:
    """Test WritingAgent class."""
    
    @pytest.fixture
    def writing_agent(self, agent_config):
        """Create writing agent instance."""
        agent_config.name = "writing"
        return WritingAgent(agent_config)
    
    def test_initialization(self, writing_agent):
        """Test writing agent initialization."""
        assert writing_agent.name == "writing"
        assert writing_agent.specialization == "writing"
    
    @pytest.mark.asyncio
    @patch('madf.utils.llm_client.LLMClient.generate')
    async def test_create_outline(self, mock_generate, writing_agent):
        """Test outline creation."""
        mock_generate.return_value = "1. Introduction\n2. Body\n3. Conclusion"
        
        task = Task(
            id="test_2",
            type="writing",
            data={
                'type': 'outline',
                'research_brief': {'synthesis': 'test'},
                'requirements': {}
            }
        )
        
        result = await writing_agent.process(task)
        
        assert result.success is True
        assert 'outline' in result.data


class TestEditingAgent:
    """Test EditingAgent class."""
    
    @pytest.fixture
    def editing_agent(self, agent_config):
        """Create editing agent instance."""
        agent_config.name = "editing"
        return EditingAgent(agent_config)
    
    def test_initialization(self, editing_agent):
        """Test editing agent initialization."""
        assert editing_agent.name == "editing"
        assert editing_agent.specialization == "editing"
    
    @pytest.mark.asyncio
    @patch('madf.utils.llm_client.LLMClient.generate')
    async def test_edit_content(self, mock_generate, editing_agent):
        """Test content editing."""
        mock_generate.return_value = "Edited content"
        
        task = Task(
            id="test_3",
            type="editing",
            data={
                'content': 'Original content',
                'style_guide': {}
            }
        )
        
        result = await editing_agent.process(task)
        
        assert result.success is True
        assert 'edited_content' in result.data


class TestVerificationAgent:
    """Test VerificationAgent class."""
    
    @pytest.fixture
    def verification_agent(self, agent_config):
        """Create verification agent instance."""
        agent_config.name = "verification"
        return VerificationAgent(agent_config)
    
    def test_initialization(self, verification_agent):
        """Test verification agent initialization."""
        assert verification_agent.name == "verification"
        assert verification_agent.specialization == "verification"
    
    @pytest.mark.asyncio
    @patch('madf.utils.llm_client.LLMClient.generate')
    async def test_verify_document(self, mock_generate, verification_agent):
        """Test document verification."""
        mock_generate.return_value = '{"score": 0.85}'
        
        task = Task(
            id="test_4",
            type="verification",
            data={
                'document': 'Test document',
                'requirements': {},
                'research_brief': 'Test brief'
            }
        )
        
        result = await verification_agent.process(task)
        
        assert result.success is True
        assert 'verification_report' in result.data