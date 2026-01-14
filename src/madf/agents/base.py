"""Base agent implementation."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

from ..models.task import Task, TaskResult
from ..utils.config import AgentConfig
from ..utils.llm_client import LLMClient

logger = logging.getLogger(__name__)


class AgentState:
    """Agent states."""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"


class BaseAgent(ABC):
    """
    Base class for all agents in the system.
    
    Provides common functionality:
    - LLM API interaction
    - Message queue management
    - State persistence
    - Error handling and retries
    - Performance metrics
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize base agent.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.name = config.name
        self.llm_client = LLMClient(config.model_config)
        self.state = AgentState.IDLE
        self.logger = logging.getLogger(f"agent.{self.name}")
        self.metrics = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_time': 0.0
        }
    
    async def execute(self, task: Task) -> TaskResult:
        """
        Execute a task with error handling and metrics.
        
        This is the main entry point for task execution.
        It wraps the process() method with common functionality.
        
        Args:
            task: Task to execute
            
        Returns:
            Task result
        """
        self.state = AgentState.BUSY
        self.logger.info(f"Starting task {task.id}")
        start_time = datetime.now()
        
        try:
            result = await self._execute_with_retry(task)
            self.metrics['tasks_completed'] += 1
            self.state = AgentState.IDLE
            
        except Exception as e:
            self.logger.error(f"Task {task.id} failed: {str(e)}")
            self.metrics['tasks_failed'] += 1
            self.state = AgentState.ERROR
            result = TaskResult(
                task_id=task.id,
                success=False,
                data={},
                error=str(e)
            )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        result.execution_time = execution_time
        self.metrics['total_time'] += execution_time
        
        return result
    
    async def _execute_with_retry(self, task: Task) -> TaskResult:
        """
        Execute task with retry logic.
        
        Args:
            task: Task to execute
            
        Returns:
            Task result
            
        Raises:
            Exception: If all retries fail
        """
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                return await asyncio.wait_for(
                    self.process(task),
                    timeout=self.config.timeout
                )
            except asyncio.TimeoutError:
                last_error = "Task timed out"
                self.logger.warning(f"Task {task.id} timed out (attempt {attempt + 1})")
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Task {task.id} failed (attempt {attempt + 1}): {e}")
            
            if attempt < self.config.max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception(f"Task failed after {self.config.max_retries} attempts: {last_error}")
    
    @abstractmethod
    async def process(self, task: Task) -> TaskResult:
        """
        Process a task and return results.
        
        This method must be implemented by each specialized agent.
        
        Args:
            task: Task to process
            
        Returns:
            Task result
        """
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get agent performance metrics.
        
        Returns:
            Dictionary of metrics
        """
        return {
            'name': self.name,
            'state': self.state,
            'metrics': self.metrics.copy()
        }