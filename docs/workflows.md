# Workflow Patterns and Best Practices

Guide to common workflow patterns and best practices for the Multi-Agent Document Framework.

## Workflow Fundamentals

### What is a Workflow?

A workflow defines:
- **Sequence** of agent tasks
- **Dependencies** between tasks
- **Data flow** between agents
- **Coordination** logic
- **Error handling** strategies

### Workflow Modes

MADF supports four execution modes:

1. **Sequential**: One agent at a time
2. **Parallel**: Multiple agents simultaneously
3. **Pipeline**: Output feeds into next agent
4. **Collaborative**: Agents communicate and iterate

## Common Workflow Patterns

### 1. Linear Sequential Workflow

**Use Case**: Step-by-step document creation

```python
from multi_agent_framework import Agent, Coordinator, WorkflowMode

# Create agents
researcher = Agent(role="researcher")
writer = Agent(role="writer")
editor = Agent(role="editor")
formatter = Agent(role="formatter")

# Setup coordinator
coordinator = Coordinator(
    agents=[researcher, writer, editor, formatter],
    workflow_mode=WorkflowMode.SEQUENTIAL
)

# Create document
document = coordinator.create_document(
    topic="Cloud Computing Trends",
    requirements={"length": "2000 words"}
)
```

**Flow**:
```
Researcher → Writer → Editor → Formatter → Final Document
```

**Advantages**:
- Simple to understand and debug
- Predictable execution
- Easy error tracking

**When to Use**:
- Small to medium documents
- When each step depends on previous
- When debugging and clarity are priorities

### 2. Parallel Workflow

**Use Case**: Independent sections created simultaneously

```python
coordinator = Coordinator(
    agents=[writer1, writer2, writer3],
    workflow_mode=WorkflowMode.PARALLEL
)

# Create custom workflow
workflow_steps = [
    {
        "agent_id": writer1.agent_id,
        "task_type": "write",
        "description": "Write Introduction section",
        "requirements": {"section": "introduction"},
    },
    {
        "agent_id": writer2.agent_id,
        "task_type": "write",
        "description": "Write Methodology section",
        "requirements": {"section": "methodology"},
    },
    {
        "agent_id": writer3.agent_id,
        "task_type": "write",
        "description": "Write Conclusion section",
        "requirements": {"section": "conclusion"},
    },
]

document = await coordinator.create_document_async(
    topic="Research Paper",
    requirements={"type": "academic"},
    workflow_steps=workflow_steps
)
```

**Flow**:
```
Writer 1 (Intro)       ↓
Writer 2 (Methods)     ↓  →  Combine  →  Final Document
Writer 3 (Conclusion)  ↓
```

**Advantages**:
- Faster execution
- Efficient resource utilization
- Good for independent tasks

**When to Use**:
- Large documents with independent sections
- Time-sensitive projects
- When sections can be written separately

### 3. Pipeline Workflow

**Use Case**: Iterative refinement of content

```python
coordinator = Coordinator(
    agents=[drafter, expander, refiner, polisher],
    workflow_mode=WorkflowMode.PIPELINE
)

# Each agent refines the previous agent's output
document = coordinator.create_document(
    topic="Product Documentation",
    requirements={
        "stages": [
            "draft_outline",
            "expand_content",
            "refine_technical_details",
            "polish_final"
        ]
    }
)
```

**Flow**:
```
Drafter → draft_v1 → Expander → draft_v2 → Refiner → draft_v3 → Polisher → Final
```

**Advantages**:
- Progressive improvement
- Each stage adds value
- Clear transformation steps

**When to Use**:
- Content that needs multiple refinement passes
- When quality improves with iterations
- Technical documentation

### 4. Collaborative Workflow

**Use Case**: Agents working together with feedback

```python
from multi_agent_framework import VerificationSystem

verification = VerificationSystem(
    checks=["quality", "factual_accuracy", "consistency"]
)

coordinator = Coordinator(
    agents=[researcher, writer, fact_checker, editor],
    workflow_mode=WorkflowMode.COLLABORATIVE,
    verification_system=verification,
    max_iterations=3
)

document = await coordinator.create_document_async(
    topic="Scientific Review Article",
    requirements={
        "enable_feedback": True,
        "min_quality_score": 0.9
    }
)
```

**Flow**:
```
Iteration 1:
  Researcher → Writer → Fact Checker → Editor
  ↓                               │
  Verification ←────────────────┘
  │
  Issues Found?
  │
Iteration 2:
  Address Issues → Verify → Done or Continue
```

**Advantages**:
- Highest quality output
- Iterative improvement
- Built-in quality control

**When to Use**:
- High-stakes documents
- When accuracy is critical
- Academic or professional publications

## Advanced Workflow Patterns

### 5. Hierarchical Workflow

**Use Case**: Complex documents with nested structure

```python
class HierarchicalWorkflow:
    def __init__(self):
        # Main coordinator
        self.main_coordinator = Coordinator(agents=[...])
        
        # Sub-coordinators for sections
        self.intro_coordinator = Coordinator(agents=[...])
        self.body_coordinator = Coordinator(agents=[...])
        self.conclusion_coordinator = Coordinator(agents=[...])
    
    async def create_document(self, requirements):
        # Create each section with its coordinator
        intro = await self.intro_coordinator.create_document_async(
            "Introduction", requirements["intro"]
        )
        
        body = await self.body_coordinator.create_document_async(
            "Main Body", requirements["body"]
        )
        
        conclusion = await self.conclusion_coordinator.create_document_async(
            "Conclusion", requirements["conclusion"]
        )
        
        # Combine with main coordinator
        final_document = self.main_coordinator.document_manager.merge_documents(
            "Complete Document",
            [intro.document_id, body.document_id, conclusion.document_id]
        )
        
        return final_document
```

### 6. Dynamic Workflow

**Use Case**: Workflow adapts based on content

```python
class DynamicWorkflow:
    async def create_document(self, topic, requirements):
        # Initial analysis
        analyzer = Agent(role="analyzer")
        analysis = await analyzer.execute_task(
            AgentTask(
                task_id="analyze",
                description=f"Analyze requirements for {topic}",
                requirements=requirements
            )
        )
        
        # Determine workflow based on analysis
        if analysis["metadata"].get("complexity") == "high":
            workflow = self._create_complex_workflow()
        elif analysis["metadata"].get("technical") == True:
            workflow = self._create_technical_workflow()
        else:
            workflow = self._create_standard_workflow()
        
        # Execute determined workflow
        return await workflow.execute(topic, requirements)
```

### 7. Quality-Gated Workflow

**Use Case**: Quality checks between stages

```python
class QualityGatedWorkflow:
    def __init__(self, verification_system):
        self.verification = verification_system
        self.coordinator = Coordinator(agents=[...])
    
    async def create_with_gates(self, topic, requirements):
        document = Document(title=topic)
        
        # Stage 1: Research
        research_result = await self._execute_stage(
            "research", document, requirements
        )
        await self._quality_gate(document, min_score=0.7)
        
        # Stage 2: Writing
        write_result = await self._execute_stage(
            "write", document, requirements
        )
        await self._quality_gate(document, min_score=0.8)
        
        # Stage 3: Editing
        edit_result = await self._execute_stage(
            "edit", document, requirements
        )
        await self._quality_gate(document, min_score=0.9)
        
        return document
    
    async def _quality_gate(self, document, min_score):
        result = self.verification.verify(document)
        if result.score < min_score:
            raise QualityGateError(
                f"Document failed quality gate: {result.score} < {min_score}"
            )
```

## Best Practices

### 1. Error Handling

```python
class RobustWorkflow:
    async def create_document_with_retry(self, topic, requirements, max_retries=3):
        for attempt in range(max_retries):
            try:
                document = await self.coordinator.create_document_async(
                    topic, requirements
                )
                return document
            except AgentError as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                # Wait before retry (exponential backoff)
                await asyncio.sleep(2 ** attempt)
```

### 2. Progress Tracking

```python
from tqdm import tqdm

class TrackedWorkflow:
    async def create_document(self, topic, requirements):
        steps = self._generate_workflow_steps(requirements)
        
        with tqdm(total=len(steps), desc="Creating document") as pbar:
            for step in steps:
                await self._execute_step(step)
                pbar.update(1)
                pbar.set_postfix({"step": step["description"]})
```

### 3. Resource Management

```python
class ResourceManagedWorkflow:
    def __init__(self, max_concurrent_agents=5):
        self.semaphore = asyncio.Semaphore(max_concurrent_agents)
        self.coordinator = Coordinator(agents=[...])
    
    async def execute_with_limit(self, tasks):
        async def limited_execute(task):
            async with self.semaphore:
                return await self.coordinator.execute_task(task)
        
        results = await asyncio.gather(
            *[limited_execute(task) for task in tasks]
        )
        return results
```

### 4. Checkpointing

```python
import json
from pathlib import Path

class CheckpointedWorkflow:
    def __init__(self, checkpoint_dir="checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
    
    async def create_document(self, topic, requirements):
        document = Document(title=topic)
        
        for i, stage in enumerate(["research", "write", "edit"]):
            # Check for existing checkpoint
            checkpoint = self._load_checkpoint(document.document_id, stage)
            if checkpoint:
                document = checkpoint
                continue
            
            # Execute stage
            await self._execute_stage(stage, document, requirements)
            
            # Save checkpoint
            self._save_checkpoint(document, stage)
        
        return document
    
    def _save_checkpoint(self, document, stage):
        checkpoint_file = self.checkpoint_dir / f"{document.document_id}_{stage}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(document.to_dict(), f)
    
    def _load_checkpoint(self, document_id, stage):
        checkpoint_file = self.checkpoint_dir / f"{document_id}_{stage}.json"
        if checkpoint_file.exists():
            with open(checkpoint_file) as f:
                data = json.load(f)
                # Reconstruct document from data
                return Document.from_dict(data)
        return None
```

### 5. Monitoring and Metrics

```python
import time
from dataclasses import dataclass, field
from typing import List

@dataclass
class WorkflowMetrics:
    start_time: float
    end_time: float = 0
    stages: List[Dict] = field(default_factory=list)
    
    @property
    def total_duration(self):
        return self.end_time - self.start_time if self.end_time else 0

class MonitoredWorkflow:
    def __init__(self):
        self.metrics = WorkflowMetrics(start_time=time.time())
        self.coordinator = Coordinator(agents=[...])
    
    async def create_document(self, topic, requirements):
        self.metrics.start_time = time.time()
        
        try:
            document = await self._create_with_monitoring(
                topic, requirements
            )
            return document
        finally:
            self.metrics.end_time = time.time()
            self._log_metrics()
    
    async def _create_with_monitoring(self, topic, requirements):
        for stage in ["research", "write", "edit"]:
            stage_start = time.time()
            
            result = await self._execute_stage(stage, requirements)
            
            self.metrics.stages.append({
                "name": stage,
                "duration": time.time() - stage_start,
                "status": "success"
            })
        
        return document
    
    def _log_metrics(self):
        logger.info(f"Workflow completed in {self.metrics.total_duration:.2f}s")
        for stage in self.metrics.stages:
            logger.info(f"  {stage['name']}: {stage['duration']:.2f}s")
```

## Workflow Selection Guide

| Document Type | Recommended Workflow | Why |
|--------------|---------------------|-----|
| Blog Post | Sequential | Simple, straightforward |
| Technical Manual | Pipeline | Needs refinement stages |
| Research Paper | Collaborative | Requires accuracy, citations |
| Marketing Content | Parallel + Review | Multiple sections, needs review |
| Legal Document | Quality-Gated | Critical accuracy requirements |
| Book Chapter | Hierarchical | Complex nested structure |

## Conclusion

Choose workflows based on:
1. **Document complexity**
2. **Time constraints**
3. **Quality requirements**
4. **Resource availability**
5. **Team size and skills**

Combine patterns as needed for optimal results.