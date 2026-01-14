"""
Agent implementation for the multi-agent document framework.

This module provides the core Agent class and related functionality for
creating specialized agents with different roles and capabilities.
"""

import asyncio
import uuid
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Predefined agent roles for document creation."""
    RESEARCHER = "researcher"
    WRITER = "writer"
    EDITOR = "editor"
    FACT_CHECKER = "fact_checker"
    REVIEWER = "reviewer"
    ANALYST = "analyst"
    FORMATTER = "formatter"
    TRANSLATOR = "translator"
    CUSTOM = "custom"


class AgentCapability(Enum):
    """Capabilities that agents can possess."""
    WEB_SEARCH = "web_search"
    DATA_ANALYSIS = "data_analysis"
    CONTENT_CREATION = "content_creation"
    PROOFREADING = "proofreading"
    FACT_VERIFICATION = "fact_verification"
    STYLE_IMPROVEMENT = "style_improvement"
    CITATION_MANAGEMENT = "citation_management"
    TECHNICAL_WRITING = "technical_writing"
    CREATIVE_WRITING = "creative_writing"
    LITERATURE_REVIEW = "literature_review"
    STATISTICAL_MODELING = "statistical_modeling"


@dataclass
class AgentMessage:
    """Message structure for agent communication."""
    sender_id: str
    recipient_id: Optional[str]
    content: str
    message_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentTask:
    """Task assigned to an agent."""
    task_id: str
    description: str
    requirements: Dict[str, Any]
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[Any] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class Agent:
    """
    Base Agent class for multi-agent document creation.
    
    Agents are specialized units that perform specific tasks in the document
    creation process. Each agent has a role, capabilities, and can communicate
    with other agents through the coordinator.
    
    Attributes:
        agent_id: Unique identifier for the agent
        role: The role this agent plays (researcher, writer, etc.)
        capabilities: List of capabilities this agent possesses
        model: The LLM model to use for this agent
        temperature: Temperature setting for LLM outputs
        max_tokens: Maximum tokens for LLM responses
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        role: str = "custom",
        capabilities: Optional[List[str]] = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.role = role
        self.capabilities = capabilities or []
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        
        self.task_history: List[AgentTask] = []
        self.message_inbox: List[AgentMessage] = []
        self.status = "idle"  # idle, working, waiting
        
        logger.info(f"Agent {self.agent_id} initialized with role: {self.role}")
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt based on agent role."""
        prompts = {
            "researcher": (
                "You are a research agent specialized in gathering, analyzing, and "
                "synthesizing information. Your task is to find accurate, relevant "
                "information and present it in a clear, organized manner."
            ),
            "writer": (
                "You are a writing agent specialized in creating clear, engaging, "
                "and well-structured content. Your task is to transform information "
                "and ideas into compelling written material."
            ),
            "editor": (
                "You are an editor agent specialized in improving content quality. "
                "Your task is to refine text for clarity, coherence, grammar, and style."
            ),
            "fact_checker": (
                "You are a fact-checking agent specialized in verifying the accuracy "
                "of information. Your task is to identify and correct factual errors."
            ),
            "reviewer": (
                "You are a review agent specialized in evaluating content quality. "
                "Your task is to provide comprehensive feedback and suggestions."
            ),
        }
        return prompts.get(self.role, "You are a helpful AI agent.")
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute a task assigned to this agent.
        
        Args:
            task: The task to execute
            
        Returns:
            Dictionary containing the task result and metadata
        """
        logger.info(f"Agent {self.agent_id} executing task: {task.task_id}")
        self.status = "working"
        task.status = "in_progress"
        
        try:
            # Simulate LLM call (in production, this would call actual LLM API)
            result = await self._process_task(task)
            
            task.status = "completed"
            task.result = result
            task.completed_at = datetime.now()
            
            self.task_history.append(task)
            self.status = "idle"
            
            logger.info(f"Agent {self.agent_id} completed task: {task.task_id}")
            
            return {
                "task_id": task.task_id,
                "status": "success",
                "result": result,
                "agent_id": self.agent_id,
            }
            
        except Exception as e:
            logger.error(f"Agent {self.agent_id} failed task {task.task_id}: {str(e)}")
            task.status = "failed"
            self.status = "idle"
            
            return {
                "task_id": task.task_id,
                "status": "failed",
                "error": str(e),
                "agent_id": self.agent_id,
            }
    
    async def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Process the task based on agent's role and capabilities.
        
        This is where the actual LLM interaction would occur in production.
        """
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # In production, this would:
        # 1. Format the task with system prompt
        # 2. Call LLM API (OpenAI, Anthropic, etc.)
        # 3. Parse and validate the response
        # 4. Return structured result
        
        result = {
            "content": f"Processed by {self.role}: {task.description}",
            "metadata": {
                "model": self.model,
                "role": self.role,
                "capabilities_used": self.capabilities,
            },
        }
        
        return result
    
    def send_message(self, message: AgentMessage) -> None:
        """Send a message to another agent (via coordinator)."""
        logger.debug(f"Agent {self.agent_id} sending message to {message.recipient_id}")
        # In production, this would go through the coordinator
        pass
    
    def receive_message(self, message: AgentMessage) -> None:
        """Receive a message from another agent."""
        logger.debug(f"Agent {self.agent_id} received message from {message.sender_id}")
        self.message_inbox.append(message)
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        return self.capabilities
    
    def can_handle_task(self, task_requirements: List[str]) -> bool:
        """Check if agent can handle a task based on requirements."""
        return any(req in self.capabilities for req in task_requirements)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and statistics."""
        completed_tasks = [t for t in self.task_history if t.status == "completed"]
        failed_tasks = [t for t in self.task_history if t.status == "failed"]
        
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "status": self.status,
            "total_tasks": len(self.task_history),
            "completed_tasks": len(completed_tasks),
            "failed_tasks": len(failed_tasks),
            "capabilities": self.capabilities,
            "messages_in_inbox": len(self.message_inbox),
        }
    
    def __repr__(self) -> str:
        return f"Agent(id={self.agent_id}, role={self.role}, status={self.status})"