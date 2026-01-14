# Agent Design and Specialization

## Overview

The Multi-Agent Document Framework employs specialized AI agents, each designed for specific aspects of document creation. This design follows the principle of **separation of concerns**, where each agent focuses on what it does best.

## Agent Architecture

### Core Design Principles

1. **Specialization**: Each agent has a specific role and expertise
2. **Autonomy**: Agents operate independently within their scope
3. **Collaboration**: Agents communicate through well-defined interfaces
4. **Resilience**: Each agent handles errors and retries independently
5. **Scalability**: Multiple agent instances can run in parallel

### Base Agent Structure

All agents inherit from `BaseAgent`, which provides:

```python
class BaseAgent(ABC):
    - LLM client for API interactions
    - State management (IDLE, BUSY, ERROR)
    - Error handling with exponential backoff
    - Performance metrics collection
    - Timeout management
    - Retry logic
```

## Specialized Agents

### 1. Research Agent

**Purpose**: Gather, validate, and synthesize information.

#### Capabilities

- **Query Decomposition**: Breaks complex topics into manageable sub-queries
- **Information Retrieval**: Gathers relevant information from multiple sources
- **Source Validation**: Assesses credibility and relevance
- **Fact Verification**: Cross-references information for accuracy
- **Data Synthesis**: Combines findings into coherent research brief

#### Process Flow

```
1. Receive research query
   ↓
2. Decompose into 3-5 sub-queries
   ↓
3. Research each sub-query independently
   ↓
4. Cross-reference findings
   ↓
5. Synthesize into research brief
   ↓
6. Structure and format output
```

#### Configuration

```yaml
research:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.3  # Low for factual accuracy
  max_tokens: 4000
  timeout: 120
```

#### Example Usage

```python
research_agent = ResearchAgent(config)
task = Task(
    id="research_1",
    type="research",
    data={
        'query': "Latest trends in renewable energy",
        'depth': 'deep',
        'focus_areas': ['solar', 'wind', 'storage']
    }
)
result = await research_agent.execute(task)
research_brief = result.data['research_brief']
```

#### Output Format

```python
{
    'research_brief': {
        'synthesis': str,  # Main research synthesis
        'timestamp': str   # ISO format timestamp
    },
    'sub_queries': List[str],  # Sub-questions researched
    'sources': List[str]       # Referenced sources
}
```

### 2. Writing Agent

**Purpose**: Transform research into well-structured, engaging content.

#### Capabilities

- **Outline Generation**: Creates hierarchical document structure
- **Section Writing**: Generates content section-by-section
- **Style Adaptation**: Adjusts tone and style for audience
- **Flow Optimization**: Ensures smooth transitions
- **Citation Management**: Integrates sources appropriately

#### Process Flow

```
1. Receive research brief and requirements
   ↓
2. Generate detailed outline
   ↓
3. Parse outline into sections
   ↓
4. Write each section with context
   ↓
5. Ensure coherent flow
   ↓
6. Assemble complete draft
```

#### Writing Modes

**Outline Mode**
```python
task_data = {
    'type': 'outline',
    'research_brief': brief,
    'requirements': {...}
}
```

**Section Mode**
```python
task_data = {
    'type': 'section',
    'section_title': 'Introduction',
    'section_outline': '...',
    'context': '...'
}
```

**Full Document Mode**
```python
task_data = {
    'type': 'full',
    'research_brief': brief,
    'requirements': {...}
}
```

#### Configuration

```yaml
writing:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.7  # Higher for creativity
  max_tokens: 8000
  timeout: 180
```

#### Output Format

```python
{
    'outline': str,  # Document outline
    'sections': List[{
        'section_title': str,
        'content': str
    }]
}
```

### 3. Editing Agent

**Purpose**: Refine and polish content for quality and clarity.

#### Capabilities

- **Structural Editing**: Improves organization and flow
- **Copy Editing**: Corrects grammar, punctuation, spelling
- **Style Editing**: Ensures consistent tone and voice
- **Readability Enhancement**: Improves clarity and engagement
- **Consistency Checking**: Enforces terminology standards

#### Multi-Pass Editing

**Pass 1: Structure and Flow**
- Logical organization
- Paragraph transitions
- Section balance
- Argument progression

**Pass 2: Grammar and Style**
- Grammar corrections
- Sentence structure
- Word choice
- Active voice preference

**Pass 3: Final Polish**
- Consistency check
- Redundancy removal
- Clarity enhancement
- Professional presentation

#### Configuration

```yaml
editing:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.5  # Moderate for balanced editing
  max_tokens: 8000
  timeout: 120
```

#### Example Usage

```python
editing_agent = EditingAgent(config)
task = Task(
    id="edit_1",
    type="editing",
    data={
        'content': draft_content,
        'style_guide': {
            'style': 'formal',
            'tone': 'professional',
            'voice': 'active'
        }
    }
)
result = await editing_agent.execute(task)
edited_content = result.data['edited_content']
```

### 4. Verification Agent

**Purpose**: Ensure accuracy, completeness, and quality.

#### Capabilities

- **Fact Checking**: Verifies claims against research
- **Completeness Analysis**: Ensures all requirements met
- **Quality Scoring**: Multi-dimensional quality assessment
- **Compliance Verification**: Checks adherence to guidelines
- **Gap Identification**: Finds missing elements

#### Verification Dimensions

**1. Factual Accuracy (35% weight)**
- Claim extraction
- Source verification
- Cross-referencing
- Contradiction detection

**2. Completeness (25% weight)**
- Section presence
- Length targets
- Topic coverage
- Detail sufficiency

**3. Quality (40% weight)**
- Coherence
- Clarity
- Readability
- Engagement
- Technical accuracy

#### Configuration

```yaml
verification:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.2  # Very low for objectivity
  max_tokens: 4000
  timeout: 120
```

#### Output Format

```python
{
    'verification_report': {
        'accuracy': {
            'score': float,  # 0-1
            'claims': List[Dict],
            'issues': List[str]
        },
        'completeness': {
            'score': float,  # 0-1
            'gaps': List[str],
            'coverage': Dict
        },
        'quality': {
            'overall_score': float,  # 0-1
            'coherence': float,
            'clarity': float,
            'readability': float,
            'engagement': float
        },
        'overall_score': float  # Weighted average
    },
    'passed': bool  # True if >= threshold
}
```

## Creating Custom Agents

### Step 1: Extend BaseAgent

```python
from madf.agents.base import BaseAgent
from madf.models.task import Task, TaskResult

class CustomAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.specialization = "custom"
        # Add custom initialization
    
    async def process(self, task: Task) -> TaskResult:
        # Implement custom logic
        result_data = await self._custom_processing(task.data)
        
        return TaskResult(
            task_id=task.id,
            success=True,
            data=result_data
        )
```

### Step 2: Register with Orchestrator

```python
orchestrator.agents['custom'] = CustomAgent(custom_config)
```

### Step 3: Use in Workflow

```python
workflow = (WorkflowBuilder()
    .add_stage("custom_stage", "custom")
    .build())
```

## Agent Communication

### Message Passing

Agents communicate through the message bus:

```python
# Agent publishes message
await self.message_bus.publish(Message(
    type=MessageType.TASK_COMPLETE,
    data={'task_id': task.id, 'result': result}
))

# Another agent subscribes
def handle_task_complete(message: Message):
    task_id = message.data['task_id']
    # Process completion

message_bus.subscribe(MessageType.TASK_COMPLETE, handle_task_complete)
```

### Data Flow

```
Research Agent
    ↓ (research_brief)
Writing Agent
    ↓ (draft_sections)
Editing Agent
    ↓ (edited_content)
Verification Agent
    ↓ (quality_report)
Orchestrator
```

## Performance Optimization

### 1. Parallel Execution

Multiple agent instances can work simultaneously:

```python
# Multiple research queries in parallel
tasks = [research_agent.execute(task) for task in research_tasks]
results = await asyncio.gather(*tasks)
```

### 2. Caching

Cache repeated LLM calls:

```python
class CachedAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(config)
        self.cache = {}
    
    async def process(self, task):
        cache_key = self._get_cache_key(task)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = await self._actual_process(task)
        self.cache[cache_key] = result
        return result
```

### 3. Resource Management

Limit concurrent agent execution:

```python
async with resource_manager.acquire('agent_1', timeout=60):
    result = await agent.execute(task)
```

## Error Handling

### Agent-Level Errors

Each agent handles its own errors:

```python
try:
    result = await agent.execute(task)
except asyncio.TimeoutError:
    # Handle timeout
except Exception as e:
    # Handle other errors
```

### Retry Strategy

Exponential backoff with maximum attempts:

```python
for attempt in range(max_retries):
    try:
        return await execute_task(task)
    except TransientError:
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)
```

## Metrics and Monitoring

### Agent Metrics

```python
metrics = agent.get_metrics()
print(f"Tasks completed: {metrics['metrics']['tasks_completed']}")
print(f"Tasks failed: {metrics['metrics']['tasks_failed']}")
print(f"Total time: {metrics['metrics']['total_time']}s")
print(f"Average time: {metrics['metrics']['total_time'] / metrics['metrics']['tasks_completed']}s")
```

### Performance Tracking

Track individual task performance:

```python
result = await agent.execute(task)
print(f"Execution time: {result.execution_time}s")
```

## Best Practices

### 1. Agent Configuration

- Use lower temperature (0.2-0.4) for factual tasks
- Use higher temperature (0.6-0.8) for creative tasks
- Set appropriate timeouts based on task complexity
- Enable caching for repeated operations

### 2. Error Handling

- Always implement retry logic
- Log errors with sufficient context
- Provide graceful degradation
- Return meaningful error messages

### 3. Resource Management

- Limit concurrent agent instances
- Monitor resource utilization
- Implement rate limiting for API calls
- Use resource pools effectively

### 4. Quality Assurance

- Validate agent inputs
- Check agent outputs
- Monitor quality scores
- Implement fallback strategies

---

**See Also**:
- [Architecture](architecture.md)
- [Coordination Protocols](coordination.md)
- [API Reference](api_reference.md)