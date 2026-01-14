# API Reference

Complete API documentation for the Multi-Agent Document Framework.

## Core Classes

### DocumentOrchestrator

The main orchestrator class for coordinating document creation.

```python
class DocumentOrchestrator:
    def __init__(self, config: OrchestratorConfig)
    async def create_document(self, request: DocumentRequest) -> Document
    async def get_document(self, document_id: str) -> Optional[Document]
    def get_agent_metrics(self) -> Dict[str, Any]
```

#### Methods

**`__init__(config: OrchestratorConfig)`**
- Initialize the orchestrator with configuration
- Parameters:
  - `config`: OrchestratorConfig instance

**`async create_document(request: DocumentRequest) -> Document`**
- Create a document from a request
- Parameters:
  - `request`: Document creation request
- Returns: Completed Document
- Raises:
  - `ValueError`: If request is invalid
  - `RuntimeError`: If creation fails

**`async get_document(document_id: str) -> Optional[Document]`**
- Retrieve a previously created document
- Parameters:
  - `document_id`: Unique document identifier
- Returns: Document if found, None otherwise

**`get_agent_metrics() -> Dict[str, Any]`**
- Get performance metrics for all agents
- Returns: Dictionary of agent metrics

### DocumentRequest

Represents a request for document creation.

```python
@dataclass
class DocumentRequest:
    topic: str
    document_type: str
    target_length: int
    style: str = "formal"
    audience: str = "general"
    requirements: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    outline: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool
```

#### Attributes

- **topic** (str): Main topic or title of the document
- **document_type** (str): Type of document (article, paper, report, etc.)
- **target_length** (int): Target word count (100-50000)
- **style** (str): Writing style (formal, casual, technical, etc.)
- **audience** (str): Target audience description
- **requirements** (List[str]): Specific requirements or sections to include
- **references** (List[str]): Optional reference materials or sources
- **outline** (Optional[str]): Optional predefined outline
- **metadata** (Dict): Additional metadata

#### Methods

**`validate() -> bool`**
- Validate request parameters
- Returns: True if valid
- Raises: ValueError with descriptive message if invalid

### Document

Represents a completed document.

```python
@dataclass
class Document:
    id: str
    title: str
    sections: List[DocumentSection]
    status: DocumentStatus
    quality_score: float = 0.0
    word_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_full_text(self) -> str
    def update_word_count(self)
    def get_section(self, title: str) -> DocumentSection
    def to_markdown(self) -> str
    def to_html(self) -> str
```

#### Attributes

- **id** (str): Unique document identifier
- **title** (str): Document title
- **sections** (List[DocumentSection]): List of document sections
- **status** (DocumentStatus): Current document status
- **quality_score** (float): Quality score (0.0-1.0)
- **word_count** (int): Total word count
- **created_at** (datetime): Creation timestamp
- **updated_at** (datetime): Last update timestamp
- **metadata** (Dict): Additional metadata

#### Methods

**`get_full_text() -> str`**
- Get complete document text with all sections
- Returns: Full text string

**`update_word_count()`**
- Update word count based on current content

**`get_section(title: str) -> DocumentSection`**
- Get section by title
- Parameters:
  - `title`: Section title
- Returns: DocumentSection
- Raises: ValueError if section not found

**`to_markdown() -> str`**
- Convert document to Markdown format
- Returns: Markdown string

**`to_html() -> str`**
- Convert document to HTML format
- Returns: HTML string

### DocumentSection

Represents a section within a document.

```python
@dataclass
class DocumentSection:
    title: str
    content: str
    order: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def word_count(self) -> int
```

### DocumentStatus

Enumeration of document statuses.

```python
class DocumentStatus(Enum):
    PENDING = "pending"
    RESEARCHING = "researching"
    WRITING = "writing"
    EDITING = "editing"
    VERIFYING = "verifying"
    COMPLETE = "complete"
    FAILED = "failed"
```

## Configuration Classes

### OrchestratorConfig

Configuration for the document orchestrator.

```python
@dataclass
class OrchestratorConfig:
    max_agents: int = 10
    timeout: int = 300
    quality_threshold: float = 0.85
    enable_parallel: bool = True
    max_concurrent_tasks: int = 5
    retry_attempts: int = 3
    research_config: Optional[AgentConfig] = None
    writing_config: Optional[AgentConfig] = None
    editing_config: Optional[AgentConfig] = None
    verification_config: Optional[AgentConfig] = None
    
    @classmethod
    def from_yaml(cls, path: str) -> 'OrchestratorConfig'
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'OrchestratorConfig'
    def save_to_yaml(self, path: str)
    def to_dict(self) -> Dict[str, Any]
```

#### Attributes

- **max_agents** (int): Maximum concurrent agents
- **timeout** (int): Overall timeout in seconds
- **quality_threshold** (float): Minimum acceptable quality score
- **enable_parallel** (bool): Enable parallel processing
- **max_concurrent_tasks** (int): Maximum concurrent tasks
- **retry_attempts** (int): Number of retry attempts
- **research_config** (AgentConfig): Research agent configuration
- **writing_config** (AgentConfig): Writing agent configuration
- **editing_config** (AgentConfig): Editing agent configuration
- **verification_config** (AgentConfig): Verification agent configuration

#### Class Methods

**`from_yaml(path: str) -> OrchestratorConfig`**
- Load configuration from YAML file
- Parameters:
  - `path`: Path to YAML file
- Returns: OrchestratorConfig instance

**`from_dict(config_dict: Dict) -> OrchestratorConfig`**
- Create configuration from dictionary
- Parameters:
  - `config_dict`: Configuration dictionary
- Returns: OrchestratorConfig instance

#### Instance Methods

**`save_to_yaml(path: str)`**
- Save configuration to YAML file
- Parameters:
  - `path`: Output file path

**`to_dict() -> Dict`**
- Convert configuration to dictionary
- Returns: Configuration dictionary

### AgentConfig

Configuration for individual agents.

```python
@dataclass
class AgentConfig:
    name: str
    model_config: ModelConfig
    timeout: int = 120
    max_retries: int = 3
    cache_enabled: bool = True
```

### ModelConfig

Configuration for LLM models.

```python
@dataclass
class ModelConfig:
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4000
    api_key: Optional[str] = None
```

## Agent Classes

### BaseAgent

Base class for all agents.

```python
class BaseAgent(ABC):
    def __init__(self, config: AgentConfig)
    async def execute(self, task: Task) -> TaskResult
    @abstractmethod
    async def process(self, task: Task) -> TaskResult
    def get_metrics(self) -> Dict[str, Any]
```

### ResearchAgent

Agent specialized in research and information gathering.

```python
class ResearchAgent(BaseAgent):
    async def process(self, task: Task) -> TaskResult
```

### WritingAgent

Agent specialized in content creation.

```python
class WritingAgent(BaseAgent):
    async def process(self, task: Task) -> TaskResult
```

### EditingAgent

Agent specialized in content refinement.

```python
class EditingAgent(BaseAgent):
    async def process(self, task: Task) -> TaskResult
```

### VerificationAgent

Agent specialized in quality assurance.

```python
class VerificationAgent(BaseAgent):
    async def process(self, task: Task) -> TaskResult
```

## Workflow Classes

### WorkflowManager

Manages workflow creation and execution.

```python
class WorkflowManager:
    def __init__()
    def create_workflow(self, request: DocumentRequest) -> Workflow
    def register_workflow(self, name: str, workflow: Workflow)
```

### WorkflowBuilder

Builder for creating custom workflows.

```python
class WorkflowBuilder:
    def __init__(self, name: str = "custom")
    def add_stage(self, name: str, agent_type: str, **kwargs) -> 'WorkflowBuilder'
    def set_metadata(self, key: str, value: any) -> 'WorkflowBuilder'
    def build(self) -> Workflow
```

#### Example

```python
workflow = (WorkflowBuilder()
    .add_stage("research", "research")
    .add_stage("writing", "writing", depends_on=["research"])
    .add_stage("editing", "editing", depends_on=["writing"])
    .build())
```

## Utility Classes

### LLMClient

Unified client for LLM API interactions.

```python
class LLMClient:
    def __init__(self, config: ModelConfig)
    async def generate(self, prompt: str, **kwargs) -> str
    def count_tokens(self, text: str) -> int
    async def generate_structured(self, prompt: str, schema: Dict) -> Dict
```

### StateStore

State storage for documents.

```python
class StateStore:
    def __init__(self, storage_path: str = "./.madf_state")
    async def save_document(self, document: Document)
    async def get_document(self, document_id: str) -> Optional[Document]
    async def delete_document(self, document_id: str)
```

### MessageBus

Event-driven message bus for agent communication.

```python
class MessageBus:
    def __init__()
    async def start()
    async def stop()
    def subscribe(self, message_type: MessageType, handler: Callable)
    def unsubscribe(self, message_type: MessageType, handler: Callable)
    async def publish(self, message: Message)
    def get_stats(self) -> Dict[str, Any]
```

### ResourceManager

Manages computational resources.

```python
class ResourceManager:
    def __init__(self, max_agents: int = 10)
    async def acquire(self, resource_id: str, timeout: Optional[float] = None) -> ResourceContext
    def release(self, resource_id: str)
    def get_stats(self) -> Dict
    def reset_metrics()
```

## Logging

### setup_logging

Configure logging for the framework.

```python
def setup_logging(level: str = "INFO", log_file: Optional[str] = None)
```

#### Parameters

- **level** (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **log_file** (Optional[str]): Optional log file path

#### Example

```python
from madf.utils.logging import setup_logging

setup_logging(level="INFO", log_file="logs/madf.log")
```

## Constants and Enums

### MessageType

```python
class MessageType(Enum):
    TASK_ASSIGNMENT = "task_assignment"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    AGENT_STATUS = "agent_status"
    QUALITY_REPORT = "quality_report"
    COORDINATION_REQUEST = "coordination_request"
    STAGE_COMPLETE = "stage_complete"
    ERROR = "error"
```

### AgentState

```python
class AgentState:
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
```

---

## Usage Examples

See the [examples/](../examples/) directory for complete working examples:

- **basic_document.py**: Simple document generation
- **research_paper.py**: Academic paper creation
- **custom_agents.py**: Creating custom agents
- **parallel_processing.py**: Multi-document generation
- **advanced_orchestration.py**: Complex workflows

## Error Handling

All async methods may raise:
- **ValueError**: Invalid parameters
- **RuntimeError**: Execution failures
- **asyncio.TimeoutError**: Operation timeouts
- **Exception**: General errors

Always wrap calls in try-except blocks for production use.