# Coordination Protocols

## Overview

The coordination layer manages communication, synchronization, and resource allocation between agents in the Multi-Agent Document Framework.

## Architecture

```
┌────────────────────────────────────────────────────┐
│              Orchestrator (Coordinator)                │
└────────────────┬────────────────────────────────────┘
                 │
     ┌───────────┼───────────┐
     │           │            │
┌────▼────┐ ┌───▼────┐ ┌──▼───┐
│Workflow│ │Message│ │Resource│
│ Manager│ │  Bus  │ │Manager│
└─────────┘ └─────────┘ └────────┘
     │           │            │
     └───────────┼───────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│          Specialized Agents (Workers)               │
│   Research | Writing | Editing | Verification       │
└────────────────────────────────────────────────────┘
```

## Components

### 1. Workflow Manager

**Purpose**: Define and execute document creation workflows.

#### Workflow Structure

```python
@dataclass
class Stage:
    name: str
    agent_type: str
    depends_on: List[str]  # Dependencies
    parallel: bool  # Can run in parallel
    optional: bool  # Can be skipped

@dataclass
class Workflow:
    name: str
    stages: List[Stage]
    metadata: Dict
```

#### Predefined Workflows

**Article Workflow**
```python
Workflow(
    name="article",
    stages=[
        Stage("research", "research"),
        Stage("writing", "writing", depends_on=["research"]),
        Stage("editing", "editing", depends_on=["writing"]),
        Stage("verification", "verification", depends_on=["editing"])
    ]
)
```

**Paper Workflow**
```python
Workflow(
    name="paper",
    stages=[
        Stage("literature_review", "research"),
        Stage("methodology", "writing", depends_on=["literature_review"]),
        Stage("results", "writing", depends_on=["methodology"]),
        Stage("editing", "editing", depends_on=["results"]),
        Stage("peer_review", "verification", depends_on=["editing"])
    ],
    metadata={'requires_citations': True}
)
```

#### Custom Workflow Creation

```python
# Using WorkflowBuilder
workflow = (WorkflowBuilder("custom")
    .add_stage("research", "research")
    .add_stage("analysis", "data_analysis", depends_on=["research"])
    .add_stage("writing", "writing", depends_on=["analysis"], parallel=True)
    .add_stage("verification", "verification", depends_on=["writing"])
    .set_metadata("custom_field", value)
    .build())

# Register workflow
workflow_manager.register_workflow("custom", workflow)
```

#### Execution Strategy

**Sequential Execution**
```
Stage 1 → Stage 2 → Stage 3 → Stage 4
```

**Parallel Execution**
```
Stage 1 → Stage 2a → Stage 3
          Stage 2b →
          Stage 2c →
```

**Conditional Execution**
```
Stage 1 → [If condition] → Stage 2a
                          → Stage 2b
```

### 2. Message Bus

**Purpose**: Enable asynchronous communication between agents.

#### Message Types

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

#### Publish/Subscribe Pattern

```python
# Publisher
await message_bus.publish(Message(
    type=MessageType.TASK_COMPLETE,
    data={'task_id': '123', 'result': {...}},
    sender='writing_agent'
))

# Subscriber
async def handle_task_complete(message: Message):
    print(f"Task {message.data['task_id']} completed")
    # Process result

message_bus.subscribe(MessageType.TASK_COMPLETE, handle_task_complete)
```

#### Message Processing

```python
class MessageBus:
    async def _process_messages(self):
        """Continuous message processing loop."""
        while self.running:
            message = await self.message_queue.get()
            await self._deliver_message(message)
    
    async def _deliver_message(self, message):
        """Deliver message to all subscribers."""
        handlers = self.subscribers.get(message.type, [])
        for handler in handlers:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Handler error: {e}")
```

#### Message Routing

```python
# Direct messaging
message = Message(
    type=MessageType.COORDINATION_REQUEST,
    data={'request': 'status'},
    sender='orchestrator',
    recipient='research_agent'  # Specific recipient
)

# Broadcast messaging
message = Message(
    type=MessageType.AGENT_STATUS,
    data={'status': 'idle'},
    sender='research_agent'
    # No recipient = broadcast
)
```

### 3. Resource Manager

**Purpose**: Manage computational resources and agent capacity.

#### Resource Pool

```python
@dataclass
class ResourcePool:
    max_size: int
    available: int
    in_use: Set[str]
    waiting: asyncio.Queue
```

#### Resource Acquisition

```python
# Acquire resource
async with resource_manager.acquire('agent_1', timeout=60) as resource:
    # Use resource
    result = await agent.execute(task)
    # Resource automatically released on exit
```

#### Load Balancing

```python
class ResourceManager:
    async def acquire_least_loaded(self) -> str:
        """Acquire least-loaded resource."""
        # Find agent with least current load
        loads = {agent_id: self._get_load(agent_id) 
                for agent_id in self.agents}
        
        least_loaded = min(loads, key=loads.get)
        return await self.acquire(least_loaded)
    
    def _get_load(self, agent_id: str) -> float:
        """Calculate current load for agent."""
        # Implementation
        pass
```

#### Capacity Planning

```python
def calculate_required_capacity(workflow, request):
    """Estimate required resources for workflow."""
    
    # Estimate based on:
    # - Document length
    # - Complexity
    # - Parallel stages
    # - Historical data
    
    base_capacity = len(workflow.stages)
    parallel_multiplier = count_parallel_stages(workflow)
    complexity_factor = estimate_complexity(request)
    
    required = base_capacity * parallel_multiplier * complexity_factor
    
    return math.ceil(required)
```

## Coordination Patterns

### 1. Sequential Coordination

Agents execute one after another:

```python
async def sequential_execution(stages, context):
    for stage in stages:
        result = await execute_stage(stage, context)
        context[stage.name] = result
    return context
```

### 2. Parallel Coordination

Multiple agents work simultaneously:

```python
async def parallel_execution(stages, context):
    tasks = [execute_stage(stage, context) for stage in stages]
    results = await asyncio.gather(*tasks)
    
    for stage, result in zip(stages, results):
        context[stage.name] = result
    
    return context
```

### 3. Pipeline Coordination

Agents form a processing pipeline:

```python
async def pipeline_execution(stages, initial_data):
    data = initial_data
    
    for stage in stages:
        data = await execute_stage(stage, data)
    
    return data
```

### 4. Hierarchical Coordination

Super-agent coordinates sub-agents:

```python
class SupervisorAgent:
    async def coordinate(self, task):
        # Decompose task
        subtasks = self.decompose_task(task)
        
        # Assign to sub-agents
        results = await asyncio.gather(*[
            self.assign_subtask(subtask, agent)
            for subtask, agent in zip(subtasks, self.sub_agents)
        ])
        
        # Aggregate results
        return self.aggregate(results)
```

## Synchronization

### Stage Dependencies

```python
class WorkflowExecutor:
    async def execute_with_dependencies(self, workflow):
        completed = set()
        pending = set(workflow.stages)
        
        while pending:
            # Find executable stages
            executable = [
                stage for stage in pending
                if stage.can_execute(completed)
            ]
            
            if not executable:
                raise DeadlockError("No executable stages")
            
            # Execute stages
            results = await asyncio.gather(*[
                self.execute_stage(stage)
                for stage in executable
            ])
            
            # Update state
            for stage in executable:
                completed.add(stage.name)
                pending.remove(stage)
```

### Barrier Synchronization

```python
class Barrier:
    def __init__(self, count):
        self.count = count
        self.waiting = 0
        self.event = asyncio.Event()
    
    async def wait(self):
        self.waiting += 1
        if self.waiting >= self.count:
            self.event.set()
        await self.event.wait()
```

## Error Handling

### Agent Failure Recovery

```python
async def execute_with_recovery(stage, context, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await execute_stage(stage, context)
        except AgentFailure as e:
            if attempt < max_retries - 1:
                # Restart agent
                await restart_agent(stage.agent_type)
                await asyncio.sleep(2 ** attempt)
            else:
                raise WorkflowError(f"Stage {stage.name} failed after {max_retries} attempts")
```

### Partial Failure Handling

```python
async def execute_with_partial_failure(stages, context):
    results = await asyncio.gather(
        *[execute_stage(s, context) for s in stages],
        return_exceptions=True
    )
    
    successful = [r for r in results if not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]
    
    if failed:
        logger.warning(f"{len(failed)} stages failed")
        # Decide: continue, retry, or abort
    
    return successful
```

## Performance Optimization

### 1. Caching

```python
class CachedWorkflowExecutor:
    def __init__(self):
        self.cache = {}
    
    async def execute_stage(self, stage, context):
        cache_key = self._get_cache_key(stage, context)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = await super().execute_stage(stage, context)
        self.cache[cache_key] = result
        return result
```

### 2. Prefetching

```python
async def execute_with_prefetch(stages, context):
    # Start next stage early
    current = stages[0]
    current_task = asyncio.create_task(execute_stage(current, context))
    
    for i, next_stage in enumerate(stages[1:], 1):
        # Wait for current
        result = await current_task
        context[current.name] = result
        
        # Start next
        current = next_stage
        current_task = asyncio.create_task(execute_stage(current, context))
    
    # Wait for last
    result = await current_task
    context[current.name] = result
```

### 3. Adaptive Scheduling

```python
class AdaptiveScheduler:
    def schedule_tasks(self, tasks):
        # Sort by priority and estimated duration
        prioritized = sorted(
            tasks,
            key=lambda t: (t.priority, -self.estimate_duration(t))
        )
        return prioritized
    
    def estimate_duration(self, task):
        # Use historical data
        similar_tasks = self.get_similar_tasks(task)
        if similar_tasks:
            return statistics.mean([t.duration for t in similar_tasks])
        return DEFAULT_DURATION
```

## Monitoring

### Coordination Metrics

```python
class CoordinationMetrics:
    def __init__(self):
        self.metrics = {
            'workflows_executed': 0,
            'stages_executed': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'resource_acquisitions': 0,
            'coordination_overhead': 0.0
        }
    
    def record_workflow(self, workflow, duration):
        self.metrics['workflows_executed'] += 1
        self.metrics['stages_executed'] += len(workflow.stages)
        # Calculate overhead
        pure_execution = sum(stage.duration for stage in workflow.stages)
        overhead = duration - pure_execution
        self.metrics['coordination_overhead'] += overhead
```

---

**See Also**:
- [Architecture](architecture.md)
- [Agent Design](agents.md)
- [API Reference](api_reference.md)