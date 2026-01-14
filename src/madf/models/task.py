"""Task models for agent execution."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class Task:
    """
    Represents a task for an agent.
    
    Attributes:
        id: Unique task identifier
        type: Task type
        data: Task payload data
        priority: Task priority (higher = more urgent)
        created_at: Task creation timestamp
        assigned_to: Agent assigned to this task
    """
    id: str
    type: str
    data: Dict[str, Any]
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    assigned_to: Optional[str] = None


@dataclass
class TaskResult:
    """
    Result from agent task execution.
    
    Attributes:
        task_id: ID of completed task
        success: Whether task succeeded
        data: Result data
        error: Error message if failed
        execution_time: Time taken to execute (seconds)
        metadata: Additional result metadata
    """
    task_id: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)