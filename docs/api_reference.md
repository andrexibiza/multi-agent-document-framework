# API Reference

Complete API documentation for the Multi-Agent Document Framework.

## Core Classes

### Agent

Base class for all agents in the framework.

#### Constructor

```python
Agent(
    agent_id: Optional[str] = None,
    role: str = "custom",
    capabilities: Optional[List[str]] = None,
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    system_prompt: Optional[str] = None
)
```

**Parameters**:
- `agent_id`: Unique identifier (generated if not provided)
- `role`: Agent role (researcher, writer, editor, etc.)
- `capabilities`: List of agent capabilities
- `model`: LLM model to use
- `temperature`: Randomness in outputs (0.0-1.0)
- `max_tokens`: Maximum response length
- `system_prompt`: Custom system prompt

**Example**:
```python
agent = Agent(
    role="researcher",
    capabilities=["web_search", "data_analysis"],
    model="gpt-4"
)
```

#### Methods

##### execute_task

```python
async execute_task(task: AgentTask) -> Dict[str, Any]
```

Execute a task assigned to this agent.

**Parameters**:
- `task`: AgentTask object containing task details

**Returns**: Dictionary with task result and metadata

**Example**:
```python
task = AgentTask(
    task_id="task_001",
    description="Research AI trends",
    requirements={"depth": "comprehensive"}
)

result = await agent.execute_task(task)
print(result["content"])
```

##### send_message

```python
send_message(message: AgentMessage) -> None
```

Send a message to another agent.

##### receive_message

```python
receive_message(message: AgentMessage) -> None
```

Receive a message from another agent.

##### get_status

```python
get_status() -> Dict[str, Any]
```

Get current agent status and statistics.

**Returns**: Dictionary with agent status information

**Example**:
```python
status = agent.get_status()
print(f"Completed tasks: {status['completed_tasks']}")
```

---

### Coordinator

Orchestrates multi-agent workflows.

#### Constructor

```python
Coordinator(
    agents: List[Agent],
    workflow_mode: WorkflowMode = WorkflowMode.SEQUENTIAL,
    verification_system: Optional[VerificationSystem] = None,
    max_iterations: int = 3,
    config: Optional[Config] = None
)
```

**Parameters**:
- `agents`: List of agents to coordinate
- `workflow_mode`: Execution mode (SEQUENTIAL, PARALLEL, etc.)
- `verification_system`: Optional verification system
- `max_iterations`: Maximum refinement iterations
- `config`: Configuration object

**Example**:
```python
coordinator = Coordinator(
    agents=[researcher, writer, editor],
    workflow_mode=WorkflowMode.SEQUENTIAL,
    max_iterations=3
)
```

#### Methods

##### create_document

```python
create_document(
    topic: str,
    requirements: Dict[str, Any],
    workflow_steps: Optional[List[Dict[str, Any]]] = None
) -> Document
```

Create a document using multi-agent collaboration (synchronous).

**Parameters**:
- `topic`: Document topic/title
- `requirements`: Document requirements dictionary
- `workflow_steps`: Optional custom workflow steps

**Returns**: Completed Document object

**Example**:
```python
document = coordinator.create_document(
    topic="AI in Healthcare",
    requirements={
        "length": "2000 words",
        "style": "technical",
        "sections": ["Introduction", "Applications", "Challenges"]
    }
)
```

##### create_document_async

```python
async create_document_async(
    topic: str,
    requirements: Dict[str, Any],
    workflow_steps: Optional[List[Dict[str, Any]]] = None
) -> Document
```

Create a document using multi-agent collaboration (asynchronous).

**Example**:
```python
document = await coordinator.create_document_async(
    topic="AI in Healthcare",
    requirements={...}
)
```

##### get_workflow_status

```python
get_workflow_status() -> Dict[str, Any]
```

Get current workflow status and statistics.

---

### Document

Represents a document being created.

#### Constructor

```python
Document(
    title: str,
    document_id: Optional[str] = None,
    requirements: Optional[Dict[str, Any]] = None
)
```

#### Properties

- `word_count`: Total word count (read-only)
- `section_count`: Number of sections (read-only)

#### Methods

##### add_section

```python
add_section(
    title: str,
    content: str,
    order: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Section
```

Add a new section to the document.

**Example**:
```python
section = document.add_section(
    title="Introduction",
    content="This paper explores...",
    metadata={"author": "researcher_01"}
)
```

##### update_section

```python
update_section(section_id: str, content: str) -> bool
```

Update content of an existing section.

##### remove_section

```python
remove_section(section_id: str) -> bool
```

Remove a section from the document.

##### create_version

```python
create_version(change_description: str, created_by: str = "system") -> DocumentVersion
```

Create a new version snapshot.

**Example**:
```python
version = document.create_version(
    change_description="Added conclusion section",
    created_by="editor_01"
)
```

##### to_markdown

```python
to_markdown() -> str
```

Export document as Markdown.

##### to_json

```python
to_json() -> str
```

Export document as JSON.

---

### DocumentManager

Manager for document lifecycle.

#### Methods

##### create_document

```python
create_document(
    title: str,
    requirements: Optional[Dict[str, Any]] = None
) -> Document
```

Create and register a new document.

##### get_document

```python
get_document(document_id: str) -> Optional[Document]
```

Retrieve a document by ID.

##### list_documents

```python
list_documents() -> List[Document]
```

List all managed documents.

##### finalize_document

```python
finalize_document(document: Document) -> None
```

Mark document as final and create version snapshot.

##### export_document

```python
export_document(
    document_id: str,
    format: str = "markdown"
) -> Optional[str]
```

Export document in specified format.

**Example**:
```python
markdown_content = manager.export_document(
    document_id="doc_123",
    format="markdown"
)
```

---

### VerificationSystem

Comprehensive document verification.

#### Constructor

```python
VerificationSystem(
    checks: Optional[List[str]] = None,
    min_overall_score: float = 0.8
)
```

**Parameters**:
- `checks`: List of checks to enable (quality, factual_accuracy, consistency, etc.)
- `min_overall_score`: Minimum score to pass verification

**Example**:
```python
verification = VerificationSystem(
    checks=["quality", "factual_accuracy", "consistency"],
    min_overall_score=0.85
)
```

#### Methods

##### verify

```python
verify(document: Document) -> VerificationResult
```

Verify a document against all enabled checks.

**Returns**: VerificationResult with score and issues

**Example**:
```python
result = verification.verify(document)
if result.passed:
    print("Document passed verification!")
else:
    print(f"Found {len(result.issues)} issues")
    for issue in result.issues:
        print(f"- {issue.description}")
```

##### get_verification_report

```python
get_verification_report(result: VerificationResult) -> str
```

Generate human-readable verification report.

---

### Config

Configuration management.

#### Class Methods

##### from_yaml

```python
@classmethod
from_yaml(cls, file_path: str) -> Config
```

Load configuration from YAML file.

**Example**:
```python
config = Config.from_yaml("config.yaml")
```

##### from_dict

```python
@classmethod
from_dict(cls, config_dict: Dict[str, Any]) -> Config
```

Create configuration from dictionary.

#### Methods

##### to_yaml

```python
to_yaml(file_path: str) -> None
```

Save configuration to YAML file.

##### setup_logging

```python
setup_logging() -> None
```

Configure logging based on settings.

---

## Enumerations

### AgentRole

```python
class AgentRole(Enum):
    RESEARCHER = "researcher"
    WRITER = "writer"
    EDITOR = "editor"
    FACT_CHECKER = "fact_checker"
    REVIEWER = "reviewer"
    ANALYST = "analyst"
    FORMATTER = "formatter"
    TRANSLATOR = "translator"
    CUSTOM = "custom"
```

### AgentCapability

```python
class AgentCapability(Enum):
    WEB_SEARCH = "web_search"
    DATA_ANALYSIS = "data_analysis"
    CONTENT_CREATION = "content_creation"
    PROOFREADING = "proofreading"
    FACT_VERIFICATION = "fact_verification"
    STYLE_IMPROVEMENT = "style_improvement"
    # ... more capabilities
```

### WorkflowMode

```python
class WorkflowMode(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    COLLABORATIVE = "collaborative"
```

---

## Data Classes

### AgentTask

```python
@dataclass
class AgentTask:
    task_id: str
    description: str
    requirements: Dict[str, Any]
    status: str = "pending"
    result: Optional[Any] = None
```

### Section

```python
@dataclass
class Section:
    title: str
    content: str
    section_id: str
    order: int = 0
    subsections: List['Section'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### VerificationResult

```python
@dataclass
class VerificationResult:
    check_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    issues: List[VerificationIssue]
    metadata: Dict[str, Any]
```

---

## Complete Example

```python
import asyncio
from multi_agent_framework import (
    Agent, Coordinator, Config,
    VerificationSystem, WorkflowMode
)

# Load configuration
config = Config.from_yaml("config.yaml")
config.setup_logging()

# Create agents
agents = [
    Agent(
        role="researcher",
        capabilities=["web_search", "literature_review"],
        model="gpt-4"
    ),
    Agent(
        role="writer",
        capabilities=["content_creation", "technical_writing"],
        model="gpt-4"
    ),
    Agent(
        role="editor",
        capabilities=["proofreading", "style_improvement"],
        model="gpt-4"
    )
]

# Setup verification
verification = VerificationSystem(
    checks=["quality", "factual_accuracy", "consistency"],
    min_overall_score=0.85
)

# Create coordinator
coordinator = Coordinator(
    agents=agents,
    workflow_mode=WorkflowMode.SEQUENTIAL,
    verification_system=verification,
    max_iterations=3,
    config=config
)

# Create document
async def main():
    document = await coordinator.create_document_async(
        topic="The Future of AI",
        requirements={
            "length": "2000 words",
            "style": "technical but accessible",
            "sections": [
                "Introduction",
                "Current State",
                "Future Trends",
                "Conclusion"
            ]
        }
    )
    
    print(f"Document created: {document.word_count} words")
    print(f"Verification score: {document.verification_score}")
    
    # Export document
    markdown = document.to_markdown()
    with open("output.md", "w") as f:
        f.write(markdown)

# Run
asyncio.run(main())
```