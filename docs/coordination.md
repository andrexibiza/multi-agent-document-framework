# Coordination Protocol

## Overview

The coordination subsystem enables seamless communication and state management across multiple agents working on document creation. It provides the infrastructure for agents to collaborate effectively without tight coupling.

## Architecture

```
┏━━━━━━━━━━━━━━━━┓     ┏━━━━━━━━━━━━━━━━┓
┃  Agent Network  ┃     ┃  Orchestrator  ┃
┗━━━━━━━━┬━━━━━━━┛     ┗━━━━━━━┬━━━━━━━━┛
         │                     │
         │                     │
         └──────┬─────────────┘
                │
       ┏━━━━━━━┴━━━━━━━━┓
       ┃  Message Bus   ┃
       ┃  (Pub/Sub)     ┃
       ┗━━━━━━━┬━━━━━━━━┛
                │
       ┏━━━━━━━┴━━━━━━━━┓
       ┃ State Manager ┃
       ┃  (Shared State)┃
       ┗━━━━━━━━━━━━━━━━┛
```

## Message Bus

### Purpose

The message bus provides asynchronous, decoupled communication between agents. Instead of agents calling each other directly, they communicate through messages, which provides:

1. **Loose Coupling**: Agents don't need to know about each other's implementation
2. **Async Communication**: Non-blocking message passing
3. **Priority Handling**: Important messages can be prioritized
4. **Reliability**: Messages can be queued and retried
5. **Observability**: All communication is logged and traceable

### Message Types

```python
class MessageType(Enum):
    TASK = "task"              # Assign new task to agent
    RESULT = "result"          # Task completion notification
    STATUS = "status"          # Status update from agent
    ERROR = "error"            # Error notification
    FEEDBACK = "feedback"      # Feedback from one agent to another
    CONTROL = "control"        # Control commands from orchestrator
```

### Message Structure

```python
@dataclass
class Message:
    id: str                          # Unique message ID
    type: MessageType                # Message type
    sender: str                      # Sending agent name
    recipient: str                   # Receiving agent name
    payload: Dict[str, Any]          # Message data
    timestamp: datetime              # When created
    priority: int                    # Priority (0-10, higher = more urgent)
    correlation_id: Optional[str]    # Links related messages
```

### Usage Examples

#### Publishing Messages

```python
# Create message bus
message_bus = MessageBus()

# Register agents
message_bus.register_agent("research", research_agent)
message_bus.register_agent("writing", writing_agent)

# Send a message
await message_bus.send(
    sender="orchestrator",
    recipient="research",
    message_type=MessageType.TASK,
    payload={
        "task_id": "research_001",
        "action": "search",
        "query": "quantum computing applications"
    },
    priority=5
)
```

#### Subscribing to Messages

```python
async def handle_result(message: Message):
    """Handle result messages"""
    if message.type == MessageType.RESULT:
        print(f"Received result from {message.sender}")
        # Process result
        result_data = message.payload

# Subscribe to results
message_bus.subscribe("result", handle_result)
```

#### Receiving Messages

```python
# Agent receives next message from its queue
message = await message_bus.receive(
    agent_name="writing",
    timeout=30.0  # Wait up to 30 seconds
)

if message:
    # Process the message
    await process_message(message)
```

### Message Flow Example

```
1. Orchestrator sends TASK message to Research Agent
   {
     "type": "TASK",
     "sender": "orchestrator",
     "recipient": "research",
     "payload": {"topic": "AI Ethics"},
     "priority": 5
   }

2. Research Agent processes and sends RESULT
   {
     "type": "RESULT",
     "sender": "research",
     "recipient": "orchestrator",
     "payload": {"research_data": {...}},
     "correlation_id": "task_001"
   }

3. Orchestrator forwards to Writing Agent
   {
     "type": "TASK",
     "sender": "orchestrator",
     "recipient": "writing",
     "payload": {"research_data": {...}},
     "priority": 5,
     "correlation_id": "task_001"
   }

4. Agents continue workflow...
```

## State Manager

### Purpose

The state manager maintains shared state across all agents, providing:

1. **Centralized State**: Single source of truth for document state
2. **Atomic Operations**: Thread-safe state updates
3. **Version Control**: Track all changes to documents
4. **History**: Complete audit trail of modifications
5. **Consistency**: Ensure all agents see consistent state

### State Types

#### Document State

```python
@dataclass
class DocumentState:
    document_id: str
    version: int
    content: str
    metadata: Dict[str, Any]
    history: List[StateChange]
    created_at: datetime
    updated_at: datetime
```

#### Workflow State

```python
@dataclass
class WorkflowState:
    workflow_id: str
    stage: str
    completed_stages: List[str]
    pending_stages: List[str]
    quality_scores: Dict[str, float]
    iteration: int
```

### Usage Examples

#### Creating Document State

```python
state_manager = StateManager()

# Create new document state
state = await state_manager.create_document_state(
    document_id="doc_001",
    topic="Machine Learning in Healthcare",
    requirements={
        "length": "3000 words",
        "tone": "professional",
        "include_citations": True
    },
    context={}
)
```

#### Updating Document Content

```python
# Agent updates document content
success = await state_manager.update_document_content(
    document_id="doc_001",
    content="# Machine Learning in Healthcare\n\nIntroduction....",
    actor="writing_agent"
)

if success:
    print("Document updated successfully")
```

#### Tracking Workflow Progress

```python
# Create workflow state
workflow = await state_manager.create_workflow_state(
    workflow_id="workflow_001",
    stages=["research", "writing", "editing", "verification"]
)

# Update current stage
await state_manager.update_stage(
    workflow_id="workflow_001",
    stage="writing"
)

# Mark stage as completed
await state_manager.complete_stage(
    workflow_id="workflow_001",
    stage="research",
    quality_score=0.92
)
```

#### Getting State History

```python
# Get complete history of changes
history = await state_manager.get_state_history("doc_001")

for change in history:
    print(f"{change.timestamp}: {change.actor} - {change.action}")
```

### State Snapshots

```python
# Create snapshot of current state
snapshot = await state_manager.snapshot_state("doc_001")

# Save snapshot (e.g., to file or database)
save_snapshot(snapshot)

# Later, restore from snapshot
await state_manager.restore_snapshot(snapshot)
```

## Communication Protocol

### Agent-to-Agent Communication

Agents communicate indirectly through the message bus:

```python
class CommunicationProtocol:
    """
    Defines communication patterns between agents.
    """
    
    @staticmethod
    async def request_response(message_bus, sender, recipient, request):
        """
        Request-response pattern.
        
        1. Send request
        2. Wait for response
        3. Return response or timeout
        """
        # Send request
        message = await message_bus.send(
            sender=sender,
            recipient=recipient,
            message_type=MessageType.TASK,
            payload=request,
            priority=5
        )
        
        # Wait for response (with correlation ID)
        timeout = 60.0
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = await message_bus.receive(sender, timeout=1.0)
            
            if response and response.correlation_id == message.id:
                return response.payload
        
        raise TimeoutError("No response received")
    
    @staticmethod
    async def broadcast(message_bus, sender, recipients, message_data):
        """
        Broadcast message to multiple recipients.
        """
        for recipient in recipients:
            await message_bus.send(
                sender=sender,
                recipient=recipient,
                message_type=MessageType.CONTROL,
                payload=message_data
            )
    
    @staticmethod
    async def publish_subscribe(message_bus, topic, message_data):
        """
        Pub/sub pattern - publish to all subscribers.
        """
        message = Message(
            type=MessageType.STATUS,
            sender="system",
            recipient="",  # Broadcast
            payload=message_data
        )
        
        await message_bus.publish(message)
```

### Synchronization Patterns

#### Sequential Workflow

```python
async def sequential_workflow(orchestrator, agents):
    """
    Execute agents in sequence: A -> B -> C
    """
    result_a = await agents['a'].execute()
    result_b = await agents['b'].execute(result_a)
    result_c = await agents['c'].execute(result_b)
    return result_c
```

#### Parallel Workflow

```python
async def parallel_workflow(orchestrator, agents):
    """
    Execute agents in parallel: A, B, C simultaneously
    """
    results = await asyncio.gather(
        agents['a'].execute(),
        agents['b'].execute(),
        agents['c'].execute()
    )
    return combine_results(results)
```

#### Fork-Join Pattern

```python
async def fork_join_workflow(orchestrator, agents):
    """
    Fork: One agent spawns multiple parallel tasks
    Join: Wait for all to complete and merge results
    """
    # Fork
    tasks = [
        agents['worker'].execute(chunk)
        for chunk in split_work()
    ]
    
    # Join
    results = await asyncio.gather(*tasks)
    return merge_results(results)
```

## Error Handling

### Message Delivery Failures

```python
try:
    await message_bus.send(
        sender="agent_a",
        recipient="agent_b",
        message_type=MessageType.TASK,
        payload=data
    )
except RecipientNotFoundError:
    # Handle unknown recipient
    logger.error("Recipient not registered")
    # Message goes to dead letter queue
```

### State Conflicts

```python
try:
    async with state_manager.locks[doc_id]:
        # Atomic update
        await state_manager.update_document_content(
            document_id=doc_id,
            content=new_content,
            actor="agent_x"
        )
except StateConflictError:
    # Handle concurrent modification
    current_state = await state_manager.get_document_state(doc_id)
    # Merge or retry
```

### Dead Letter Queue

```python
# Check for undeliverable messages
dead_letters = message_bus.get_dead_letters()

for message in dead_letters:
    logger.warning(f"Undeliverable message: {message.id}")
    # Retry or handle appropriately
    await handle_dead_letter(message)
```

## Performance Optimization

### Message Batching

```python
async def batch_messages(message_bus, messages):
    """
    Send multiple messages efficiently.
    """
    tasks = [
        message_bus.publish(msg)
        for msg in messages
    ]
    await asyncio.gather(*tasks)
```

### State Caching

```python
class CachedStateManager(StateManager):
    def __init__(self):
        super().__init__()
        self.cache = {}
        self.cache_ttl = 60  # seconds
    
    async def get_document_state(self, document_id):
        # Check cache first
        if document_id in self.cache:
            cached, timestamp = self.cache[document_id]
            if time.time() - timestamp < self.cache_ttl:
                return cached
        
        # Fetch from storage
        state = await super().get_document_state(document_id)
        self.cache[document_id] = (state, time.time())
        return state
```

### Connection Pooling

```python
class PooledMessageBus(MessageBus):
    def __init__(self, pool_size=10):
        super().__init__()
        self.connection_pool = ConnectionPool(pool_size)
    
    async def send(self, *args, **kwargs):
        async with self.connection_pool.acquire() as connection:
            return await super().send(*args, **kwargs)
```

## Monitoring

### Message Metrics

```python
class MonitoredMessageBus(MessageBus):
    def __init__(self):
        super().__init__()
        self.metrics = {
            'messages_sent': 0,
            'messages_received': 0,
            'average_latency': 0.0,
            'errors': 0
        }
    
    async def send(self, *args, **kwargs):
        start = time.time()
        try:
            result = await super().send(*args, **kwargs)
            self.metrics['messages_sent'] += 1
            latency = time.time() - start
            self._update_latency(latency)
            return result
        except Exception as e:
            self.metrics['errors'] += 1
            raise
```

### State Metrics

```python
metrics = {
    'active_documents': len(state_manager.document_states),
    'active_workflows': len(state_manager.workflow_states),
    'total_state_changes': sum(
        len(state.history) 
        for state in state_manager.document_states.values()
    ),
    'average_document_version': sum(
        state.version 
        for state in state_manager.document_states.values()
    ) / max(len(state_manager.document_states), 1)
}
```

## Best Practices

### 1. Message Design
- Keep payloads small and focused
- Use correlation IDs to link related messages
- Set appropriate priorities
- Include timestamps for debugging

### 2. State Management
- Always use locks for concurrent updates
- Keep state history bounded (delete old entries)
- Create snapshots before major operations
- Validate state before updates

### 3. Error Recovery
- Implement retry logic with exponential backoff
- Use dead letter queues for failed messages
- Log all errors with context
- Have fallback mechanisms

### 4. Testing
- Test message ordering
- Test concurrent state updates
- Test failure scenarios
- Test message loss/duplication

---

The coordination system is the backbone of the multi-agent framework, enabling scalable, reliable communication and state management across all components.