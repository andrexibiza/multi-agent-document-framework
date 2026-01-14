# Agent Design Guide

Comprehensive guide for designing and implementing custom agents in the Multi-Agent Document Framework.

## Agent Fundamentals

### What is an Agent?

An agent in MADF is an autonomous unit that:
- Has a specific **role** (researcher, writer, editor, etc.)
- Possesses certain **capabilities** (web search, proofreading, etc.)
- Processes **tasks** independently
- Can **communicate** with other agents
- Maintains its own **state** and **history**

### Agent Lifecycle

```
1. Initialization
   ↓
2. Idle (waiting for tasks)
   ↓
3. Task Assignment
   ↓
4. Working (processing task)
   ↓
5. Task Completion
   ↓
6. Back to Idle or Shutdown
```

## Creating Custom Agents

### Basic Custom Agent

```python
from multi_agent_framework import Agent, AgentTask
import asyncio

class SummarizerAgent(Agent):
    """
    Agent specialized in creating concise summaries.
    """
    
    def __init__(self, agent_id=None):
        super().__init__(
            agent_id=agent_id,
            role="summarizer",
            capabilities=["text_summarization", "key_points_extraction"],
            model="gpt-4",
            temperature=0.3,  # Lower temperature for more focused output
        )
    
    def _get_default_system_prompt(self):
        return (
            "You are a summarization specialist. Your task is to create "
            "clear, concise summaries that capture the essential points "
            "of the content while maintaining accuracy."
        )
    
    async def _process_task(self, task: AgentTask):
        # Custom processing logic
        content = task.requirements.get("content", "")
        max_length = task.requirements.get("max_length", 200)
        
        # In production, this would call LLM API
        summary = await self._generate_summary(content, max_length)
        
        return {
            "content": summary,
            "metadata": {
                "original_length": len(content.split()),
                "summary_length": len(summary.split()),
                "compression_ratio": len(summary) / len(content) if content else 0,
            },
        }
    
    async def _generate_summary(self, content: str, max_length: int) -> str:
        # Simulate LLM call
        await asyncio.sleep(0.5)
        
        # In production:
        # response = await openai.ChatCompletion.acreate(...)
        # return response.choices[0].message.content
        
        return f"Summary of {len(content.split())} words..."

# Usage
summarizer = SummarizerAgent()
task = AgentTask(
    task_id="sum_001",
    description="Summarize research paper",
    requirements={
        "content": "Long research paper text...",
        "max_length": 150
    }
)

result = await summarizer.execute_task(task)
print(result["content"])
```

### Advanced Custom Agent with External APIs

```python
import aiohttp
from multi_agent_framework import Agent, AgentTask

class WebResearchAgent(Agent):
    """
    Agent that can perform web searches and extract information.
    """
    
    def __init__(self, api_key: str, agent_id=None):
        super().__init__(
            agent_id=agent_id,
            role="web_researcher",
            capabilities=["web_search", "url_scraping", "data_extraction"],
        )
        self.api_key = api_key
    
    async def _process_task(self, task: AgentTask):
        query = task.requirements.get("query")
        num_results = task.requirements.get("num_results", 5)
        
        # Search web
        search_results = await self._search_web(query, num_results)
        
        # Extract information
        extracted_data = await self._extract_information(search_results)
        
        # Synthesize findings
        synthesis = await self._synthesize(extracted_data)
        
        return {
            "content": synthesis,
            "metadata": {
                "sources": [r["url"] for r in search_results],
                "num_sources": len(search_results),
            },
        }
    
    async def _search_web(self, query: str, num_results: int):
        # In production, integrate with search API
        # Example: Google Custom Search, Bing Search API, etc.
        async with aiohttp.ClientSession() as session:
            # Simulated for example
            return [
                {"url": f"https://example.com/result{i}", "title": f"Result {i}"}
                for i in range(num_results)
            ]
    
    async def _extract_information(self, search_results):
        # Extract and structure information from sources
        extracted = []
        for result in search_results:
            # In production: scrape and extract content
            extracted.append({
                "source": result["url"],
                "content": "Extracted content...",
            })
        return extracted
    
    async def _synthesize(self, extracted_data):
        # Use LLM to synthesize information
        # In production: call LLM with extracted data
        return "Synthesized research findings..."
```

### Agent with Memory and Context

```python
from collections import deque
from multi_agent_framework import Agent

class ContextAwareAgent(Agent):
    """
    Agent that maintains conversation context and memory.
    """
    
    def __init__(self, memory_size=10, agent_id=None):
        super().__init__(
            agent_id=agent_id,
            role="context_aware_writer",
            capabilities=["content_creation", "context_maintenance"],
        )
        self.memory_size = memory_size
        self.context_memory = deque(maxlen=memory_size)
    
    async def _process_task(self, task: AgentTask):
        # Add current task to memory
        self.context_memory.append({
            "task_id": task.task_id,
            "description": task.description,
            "timestamp": task.created_at,
        })
        
        # Build context from memory
        context = self._build_context()
        
        # Process with context awareness
        result = await self._process_with_context(task, context)
        
        return result
    
    def _build_context(self):
        """Build context string from memory."""
        if not self.context_memory:
            return ""
        
        context_parts = ["Previous tasks:"]
        for item in self.context_memory:
            context_parts.append(f"- {item['description']}")
        
        return "\n".join(context_parts)
    
    async def _process_with_context(self, task, context):
        # In production: include context in LLM prompt
        return {
            "content": f"Content considering context: {context}",
            "metadata": {"context_items": len(self.context_memory)},
        }
```

## Agent Design Patterns

### 1. Specialist Pattern

Agents highly specialized in one task:

```python
class CitationAgent(Agent):
    """Specialized in managing citations."""
    
    def __init__(self, citation_style="APA"):
        super().__init__(
            role="citation_specialist",
            capabilities=["citation_formatting", "bibliography_generation"],
        )
        self.citation_style = citation_style
    
    async def format_citation(self, source_info):
        """Format a single citation."""
        # Implementation specific to citation style
        pass
    
    async def generate_bibliography(self, citations):
        """Generate full bibliography."""
        pass
```

### 2. Generalist Pattern

Agents that can handle multiple related tasks:

```python
class ContentAgent(Agent):
    """Generalist agent for content tasks."""
    
    def __init__(self):
        super().__init__(
            role="content_generalist",
            capabilities=[
                "writing",
                "editing",
                "formatting",
                "summarization",
            ],
        )
    
    async def _process_task(self, task):
        task_type = task.requirements.get("type")
        
        if task_type == "write":
            return await self._write_content(task)
        elif task_type == "edit":
            return await self._edit_content(task)
        elif task_type == "format":
            return await self._format_content(task)
        else:
            return await self._default_process(task)
```

### 3. Coordinator Pattern

Agents that coordinate other agents:

```python
class SupervisorAgent(Agent):
    """Agent that supervises and coordinates other agents."""
    
    def __init__(self, supervised_agents):
        super().__init__(
            role="supervisor",
            capabilities=["task_delegation", "quality_control"],
        )
        self.supervised_agents = supervised_agents
    
    async def delegate_task(self, task):
        """Delegate task to appropriate agent."""
        # Find best agent for task
        best_agent = self._find_best_agent(task)
        
        # Assign and monitor
        result = await best_agent.execute_task(task)
        
        # Verify quality
        if not self._meets_quality_standards(result):
            # Reassign or refine
            result = await self._refine_result(result)
        
        return result
```

### 4. Pipeline Pattern

Agents designed to work in sequence:

```python
class DataCollectorAgent(Agent):
    """First stage: collect data."""
    pass

class DataAnalyzerAgent(Agent):
    """Second stage: analyze collected data."""
    pass

class ReportGeneratorAgent(Agent):
    """Third stage: generate report from analysis."""
    pass

# Usage in pipeline
collected = await collector.execute_task(collection_task)
analyzed = await analyzer.execute_task(analysis_task_with(collected))
report = await generator.execute_task(report_task_with(analyzed))
```

## Best Practices

### 1. Single Responsibility

Each agent should have one clear purpose:

```python
# Good: Focused agent
class ProofreadingAgent(Agent):
    """Only handles proofreading."""
    pass

# Avoid: Agent doing too much
class DoEverythingAgent(Agent):
    """Tries to do research, write, edit, format, etc."""
    pass
```

### 2. Proper Error Handling

```python
class RobustAgent(Agent):
    async def _process_task(self, task):
        try:
            result = await self._do_processing(task)
            return result
        except APIError as e:
            logger.error(f"API error: {e}")
            # Retry logic
            return await self._retry_with_backoff(task)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return self._create_error_result(e)
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise
```

### 3. Configurable Behavior

```python
class ConfigurableAgent(Agent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            role=config.get("role", "custom"),
            model=config.get("model", "gpt-4"),
            temperature=config.get("temperature", 0.7),
        )
        self.custom_settings = config.get("custom_settings", {})
    
    @classmethod
    def from_config_file(cls, file_path: str):
        """Create agent from configuration file."""
        with open(file_path) as f:
            config = yaml.safe_load(f)
        return cls(config)
```

### 4. Testability

```python
class TestableAgent(Agent):
    def __init__(self, llm_client=None):
        super().__init__(role="testable")
        # Allow dependency injection for testing
        self.llm_client = llm_client or default_llm_client()
    
    async def _process_task(self, task):
        # Use injected client (can be mocked in tests)
        response = await self.llm_client.complete(task.description)
        return {"content": response}

# In tests:
class MockLLMClient:
    async def complete(self, prompt):
        return "Mocked response"

agent = TestableAgent(llm_client=MockLLMClient())
```

### 5. Logging and Observability

```python
import logging

class ObservableAgent(Agent):
    def __init__(self):
        super().__init__(role="observable")
        self.logger = logging.getLogger(f"agent.{self.agent_id}")
    
    async def execute_task(self, task):
        self.logger.info(f"Starting task: {task.task_id}")
        start_time = time.time()
        
        try:
            result = await super().execute_task(task)
            duration = time.time() - start_time
            
            self.logger.info(
                f"Task completed: {task.task_id} in {duration:.2f}s"
            )
            return result
        except Exception as e:
            self.logger.error(
                f"Task failed: {task.task_id} - {str(e)}"
            )
            raise
```

## Integration with LLM Providers

### OpenAI Integration

```python
import openai

class OpenAIAgent(Agent):
    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        openai.api_key = api_key
    
    async def _process_task(self, task):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task.description}
        ]
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        
        return {
            "content": response.choices[0].message.content,
            "metadata": {
                "model": self.model,
                "tokens_used": response.usage.total_tokens,
            },
        }
```

### Anthropic Integration

```python
import anthropic

class AnthropicAgent(Agent):
    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def _process_task(self, task):
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "user", "content": task.description}
            ],
        )
        
        return {
            "content": response.content[0].text,
            "metadata": {
                "model": self.model,
                "stop_reason": response.stop_reason,
            },
        }
```

## Performance Optimization

### Caching Responses

```python
from functools import lru_cache
import hashlib

class CachedAgent(Agent):
    def __init__(self):
        super().__init__(role="cached")
        self.cache = {}
    
    async def _process_task(self, task):
        # Create cache key
        cache_key = self._create_cache_key(task)
        
        # Check cache
        if cache_key in self.cache:
            logger.info(f"Cache hit for task: {task.task_id}")
            return self.cache[cache_key]
        
        # Process and cache
        result = await super()._process_task(task)
        self.cache[cache_key] = result
        
        return result
    
    def _create_cache_key(self, task):
        content = f"{task.description}{str(task.requirements)}"
        return hashlib.md5(content.encode()).hexdigest()
```

### Batch Processing

```python
class BatchAgent(Agent):
    def __init__(self, batch_size=10):
        super().__init__(role="batch_processor")
        self.batch_size = batch_size
        self.pending_tasks = []
    
    async def execute_task(self, task):
        self.pending_tasks.append(task)
        
        if len(self.pending_tasks) >= self.batch_size:
            return await self._process_batch()
        
        return None  # Will be processed in batch later
    
    async def _process_batch(self):
        tasks = self.pending_tasks[:self.batch_size]
        self.pending_tasks = self.pending_tasks[self.batch_size:]
        
        # Process all tasks in one API call
        results = await self._batch_llm_call(tasks)
        
        return results
```

## Conclusion

Effective agent design in MADF requires:
1. Clear role definition and specialization
2. Proper error handling and logging
3. Testable and maintainable code
4. Efficient integration with LLM providers
5. Performance optimization where needed

Follow these patterns and best practices to create robust, efficient agents for your multi-agent document creation system.