"""
Core data models for the framework.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import uuid


class MessageType(Enum):
    """Types of messages exchanged between agents"""
    TASK = "task"
    RESULT = "result"
    STATUS = "status"
    ERROR = "error"
    FEEDBACK = "feedback"
    CONTROL = "control"


class AgentStatus(Enum):
    """Agent operational status"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class AgentMetrics:
    """Performance metrics for an agent"""
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_processing_time: float = 0.0
    total_tokens_used: int = 0
    average_quality_contribution: float = 0.0
    last_activity: Optional[datetime] = None


@dataclass
class Task:
    """Task definition for agent processing"""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    context: Dict[str, Any]
    priority: int = 0
    timeout: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Result:
    """Result of agent processing"""
    task_id: str
    success: bool
    output: Any
    metadata: Dict[str, Any]
    metrics: Dict[str, Any]
    errors: Optional[List[str]] = None
    completed_at: datetime = field(default_factory=datetime.now)


@dataclass
class Message:
    """Message for inter-agent communication"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.TASK
    sender: str = ""
    recipient: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 0
    correlation_id: Optional[str] = None


@dataclass
class Document:
    """Document model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: str = "draft"
    
    def word_count(self) -> int:
        """Calculate word count"""
        return len(self.content.split())
    
    def character_count(self) -> int:
        """Calculate character count"""
        return len(self.content)


@dataclass
class Context:
    """Context for document creation"""
    topic: str
    requirements: Dict[str, Any]
    research_data: Optional[Dict[str, Any]] = None
    outline: Optional[Dict[str, Any]] = None
    feedback: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateChange:
    """Record of a state change"""
    timestamp: datetime = field(default_factory=datetime.now)
    actor: str = ""
    action: str = ""
    previous_state: Any = None
    new_state: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentState:
    """State of a document in creation"""
    document_id: str
    version: int = 1
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[StateChange] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowState:
    """State of workflow execution"""
    workflow_id: str
    stage: str
    completed_stages: List[str] = field(default_factory=list)
    pending_stages: List[str] = field(default_factory=list)
    quality_scores: Dict[str, float] = field(default_factory=dict)
    iteration: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
