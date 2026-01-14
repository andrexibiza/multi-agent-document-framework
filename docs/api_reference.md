# API Reference

## Core Classes

### DocumentOrchestrator

Main orchestrator for coordinating multi-agent document creation.

```python
class DocumentOrchestrator:
    def __init__(self,
                 agents: Dict[str, BaseAgent],
                 config: Optional[OrchestratorConfig] = None)
```

**Parameters:**
- `agents`: Dictionary mapping agent roles to agent instances
- `config`: Orchestrator configuration (optional)

**Methods:**

#### create_document

```python
async def create_document(self,
                         topic: str,
                         requirements: Dict[str, Any]) -> DocumentResult
```

Create a document using multi-agent collaboration.

**Parameters:**
- `topic` (str): Main topic/subject of the document
- `requirements` (Dict[str, Any]): Document requirements including:
  - `length`: Target word count (e.g., "2000-3000 words")
  - `tone`: Writing tone (e.g., "professional", "casual")
  - `style`: Writing style (e.g., "technical", "narrative")
  - `target_audience`: Intended audience
  - `include_citations`: Whether to include citations (bool)
  - Other custom requirements

**Returns:**
- `DocumentResult`: Object containing generated document and metadata

**Example:**
```python
orchestrator = DocumentOrchestrator(agents=agents, config=config)

result = await orchestrator.create_document(
    topic="Artificial Intelligence in Healthcare",
    requirements={
        "length": "2000-3000 words",
        "tone": "professional",
        "target_audience": "healthcare professionals",
        "include_citations": True
    }
)
```

#### get_agent_metrics

```python
def get_agent_metrics(self) -> Dict[str, AgentMetrics]
```

Get performance metrics from all agents.

**Returns:**
- `Dict[str, AgentMetrics]`: Metrics for each agent

#### shutdown

```python
async def shutdown(self)
```

Gracefully shutdown orchestrator and cleanup resources.

---

### OrchestratorConfig

Configuration for document orchestrator.

```python
@dataclass
class OrchestratorConfig:
    max_iterations: int = 3
    quality_threshold: float = 0.85
    enable_verification: bool = True
    enable_parallel_processing: bool = True
    timeout_seconds: int = 600
    research_timeout: int = 120
    writing_timeout: int = 180
    editing_timeout: int = 120
    verification_timeout: int = 60
    enable_caching: bool = True
    log_level: str = "INFO"
```

**Fields:**
- `max_iterations`: Maximum workflow iterations for quality improvement
- `quality_threshold`: Minimum quality score to accept (0-1)
- `enable_verification`: Enable quality verification
- `enable_parallel_processing`: Enable parallel agent execution
- `timeout_seconds`: Overall workflow timeout
- `research_timeout`: Research agent timeout
- `writing_timeout`: Writing agent timeout
- `editing_timeout`: Editing agent timeout
- `verification_timeout`: Verification agent timeout
- `enable_caching`: Enable result caching
- `log_level`: Logging level

---

## Agent Classes

### BaseAgent

Abstract base class for all agents.

```python
class BaseAgent(ABC):
    def __init__(self,
                 name: str,
                 model: str,
                 config: Optional[Dict[str, Any]] = None)
```

**Methods:**

#### process

```python
@abstractmethod
async def process(self, task: Task) -> Result
```

Process a task and return result. Must be implemented by subclasses.

#### handle_task

```python
async def handle_task(self, task: Task) -> Result
```

Main task handling with error handling and metrics tracking.

#### get_metrics

```python
def get_metrics(self) -> AgentMetrics
```

Return current performance metrics.

---

### ResearchAgent

Agent specialized in information gathering and research.

```python
class ResearchAgent(BaseAgent):
    def __init__(self,
                 model: str = "gpt-4",
                 config: Optional[Dict[str, Any]] = None)
```

**Configuration Options:**
- `temperature`: LLM temperature (default: 0.3)
- `max_sources`: Maximum number of sources to use
- `search_api_key`: API key for search service
- `source_types`: List of acceptable source types

**Expected Task Payload:**
```python
{
    "topic": str,
    "requirements": {
        "depth": "basic" | "intermediate" | "advanced",
        "focus_areas": List[str],
        "required_sources": int,
        "source_types": List[str]
    }
}
```

**Output:**
```python
{
    "key_facts": List[str],
    "sources": List[Dict],
    "themes": List[str],
    "context": Dict
}
```

---

### WritingAgent

Agent specialized in content creation and document writing.

```python
class WritingAgent(BaseAgent):
    def __init__(self,
                 model: str = "gpt-4",
                 config: Optional[Dict[str, Any]] = None)
```

**Expected Task Payload:**
```python
{
    "research_context": Dict,
    "requirements": {
        "length": str,
        "tone": str,
        "style": str,
        "target_audience": str,
        "structure": Optional[List[str]]
    }
}
```

**Output:**
```python
{
    "document": str,
    "outline": Dict,
    "word_count": int
}
```

---

### EditingAgent

Agent specialized in document editing and refinement.

```python
class EditingAgent(BaseAgent):
    def __init__(self,
                 model: str = "gpt-4",
                 config: Optional[Dict[str, Any]] = None)
```

**Expected Task Payload:**
```python
{
    "document": str,
    "requirements": {
        "tone": str,
        "style_guide": Optional[str],
        "readability_target": Optional[str],
        "preserve_structure": bool
    }
}
```

**Output:**
```python
{
    "edited_document": str,
    "changes": List[Dict]
}
```

---

### VerificationAgent

Agent specialized in document verification and quality assurance.

```python
class VerificationAgent(BaseAgent):
    def __init__(self,
                 model: str = "gpt-4",
                 config: Optional[Dict[str, Any]] = None)
```

**Expected Task Payload:**
```python
{
    "document": str,
    "research_context": Dict,
    "requirements": Dict,
    "quality_threshold": float
}
```

**Output:**
```python
{
    "overall_score": float,
    "passes_threshold": bool,
    "fact_check": Dict,
    "quality_check": Dict,
    "consistency_check": Dict,
    "feedback": Optional[Dict]
}
```

---

## Data Models

### Task

Task definition for agent processing.

```python
@dataclass
class Task:
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    context: Dict[str, Any]
    priority: int = 0
    timeout: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
```

### Result

Result of agent processing.

```python
@dataclass
class Result:
    task_id: str
    success: bool
    output: Any
    metadata: Dict[str, Any]
    metrics: Dict[str, Any]
    errors: Optional[List[str]] = None
    completed_at: datetime = field(default_factory=datetime.now)
```

### DocumentResult

Result of document creation.

```python
@dataclass
class DocumentResult:
    document_id: str
    success: bool
    content: str
    quality_score: float
    iterations: int
    metadata: Dict[str, Any]
    metrics: Dict[str, Any]
    errors: Optional[List[str]] = None
    created_at: datetime = field(default_factory=datetime.now)
```

### AgentMetrics

Performance metrics for an agent.

```python
@dataclass
class AgentMetrics:
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_processing_time: float = 0.0
    total_tokens_used: int = 0
    average_quality_contribution: float = 0.0
    last_activity: Optional[datetime] = None
```

---

## Coordination System

### MessageBus

Asynchronous message bus for agent communication.

```python
class MessageBus:
    def __init__(self)
```

**Methods:**

#### register_agent

```python
def register_agent(self, agent_name: str, agent: Any)
```

Register an agent with the message bus.

#### send

```python
async def send(self,
               sender: str,
               recipient: str,
               message_type: MessageType,
               payload: Dict[str, Any],
               priority: int = 0) -> Message
```

Send a message to a specific recipient.

#### publish

```python
async def publish(self, message: Message)
```

Publish a message to the bus.

#### subscribe

```python
def subscribe(self, topic: str, callback: Callable)
```

Subscribe to messages on a topic.

---

### StateManager

Manages shared state across agents.

```python
class StateManager:
    def __init__(self, backend: str = "memory")
```

**Methods:**

#### create_document_state

```python
async def create_document_state(self,
                               document_id: str,
                               topic: str,
                               requirements: Dict[str, Any],
                               context: Dict[str, Any]) -> DocumentState
```

#### update_document_content

```python
async def update_document_content(self,
                                 document_id: str,
                                 content: str,
                                 actor: str) -> bool
```

#### get_document_state

```python
async def get_document_state(self, document_id: str) -> Optional[DocumentState]
```

#### snapshot_state

```python
async def snapshot_state(self, document_id: str) -> Optional[Dict[str, Any]]
```

---

## Workflows

### WorkflowBuilder

Builder for creating custom workflows.

```python
class WorkflowBuilder:
    def __init__(self)
```

**Methods:**

```python
def add_stage(self, name: str, **kwargs) -> WorkflowBuilder
def add_condition(self, name: str, **kwargs) -> WorkflowBuilder  
def add_loop(self, max_iterations: int) -> WorkflowBuilder
def build(self) -> Workflow
```

**Example:**
```python
workflow = WorkflowBuilder() \
    .add_stage("research", parallel=True) \
    .add_stage("writing") \
    .add_stage("editing") \
    .add_condition("quality_check", threshold=0.9) \
    .add_stage("verification") \
    .add_loop(max_iterations=3) \
    .build()
```

---

## Utilities

### LLMWrapper

Wrapper for LLM API integration.

```python
class LLMWrapper:
    def __init__(self,
                 model: str,
                 temperature: float = 0.7,
                 max_tokens: int = 2000)
    
    async def generate(self, prompt: str) -> str
    async def generate_with_schema(self, prompt: str, schema: Dict) -> Dict
    def get_token_count(self) -> int
```

---

## Error Handling

### Exception Classes

```python
class MADFException(Exception):
    """Base exception for framework"""
    pass

class AgentException(MADFException):
    """Agent-related errors"""
    pass

class WorkflowException(MADFException):
    """Workflow execution errors"""
    pass

class VerificationException(MADFException):
    """Verification failures"""
    pass

class TimeoutException(MADFException):
    """Operation timeout"""
    pass
```

---

## Environment Variables

```bash
# LLM API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Search API
SEARCH_API_KEY=your_search_key

# Configuration
MADF_LOG_LEVEL=INFO
MADF_ENABLE_CACHE=true
MADF_CACHE_TTL=3600

# Performance
MADF_MAX_CONCURRENT_AGENTS=10
MADF_DEFAULT_TIMEOUT=600
```

---

For more examples and detailed usage, see the [examples](../examples/) directory.