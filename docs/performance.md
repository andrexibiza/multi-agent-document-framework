# Performance Tuning and Optimization

## Overview

This guide provides strategies for optimizing the performance of the Multi-Agent Document Framework.

## Performance Metrics

### Key Metrics

1. **Throughput**: Documents generated per hour
2. **Latency**: Time from request to completion
3. **Quality**: Average quality score
4. **Resource Utilization**: Agent and API usage
5. **Cost**: API costs per document

### Measurement

```python
import time
from madf import DocumentOrchestrator

start_time = time.time()
document = await orchestrator.create_document(request)
latency = time.time() - start_time

print(f"Latency: {latency:.2f}s")
print(f"Quality: {document.quality_score:.2f}")
print(f"Throughput: {3600/latency:.2f} docs/hour")
```

## Optimization Strategies

### 1. Parallel Processing

**Enable parallel agent execution:**

```python
config = OrchestratorConfig(
    enable_parallel=True,
    max_concurrent_tasks=10
)
```

**Batch document generation:**

```python
requests = [create_request(topic) for topic in topics]
tasks = [orchestrator.create_document(req) for req in requests]
documents = await asyncio.gather(*tasks)
```

### 2. Resource Management

**Increase agent pool:**

```python
config = OrchestratorConfig(
    max_agents=20  # More agents = more parallelism
)
```

**Monitor utilization:**

```python
stats = orchestrator.resource_manager.get_stats()
print(f"Utilization: {stats['utilization']:.1%}")
print(f"Peak usage: {stats['peak_usage']}/{stats['max_agents']}")
```

### 3. Caching

**Enable agent-level caching:**

```python
agent_config = AgentConfig(
    name="research",
    model_config=model_config,
    cache_enabled=True
)
```

**Implement custom caching:**

```python
from functools import lru_cache

class CachedAgent(BaseAgent):
    @lru_cache(maxsize=100)
    async def process_cached(self, task_key):
        return await self.process(task)
```

### 4. Model Selection

**Use appropriate models:**

```yaml
agents:
  research:
    model: "gpt-4"  # High accuracy needed
  writing:
    model: "gpt-4"
  editing:
    model: "gpt-3.5-turbo"  # Faster, cheaper
  verification:
    model: "gpt-4"  # High accuracy needed
```

### 5. Token Optimization

**Reduce token usage:**

```python
# Shorter prompts
prompt = f"Summarize: {text[:1000]}"  # Limit input

# Lower max_tokens
config = ModelConfig(
    max_tokens=2000  # Reduce if appropriate
)
```

**Monitor token usage:**

```python
tokens = llm_client.count_tokens(prompt)
print(f"Prompt tokens: {tokens}")
```

### 6. Timeout Management

**Set appropriate timeouts:**

```python
config = OrchestratorConfig(
    timeout=300,  # Overall timeout
    research_config=AgentConfig(
        timeout=120  # Per-agent timeout
    )
)
```

### 7. Quality vs. Speed Tradeoff

**Adjust quality threshold:**

```python
# Higher quality (slower)
config = OrchestratorConfig(
    quality_threshold=0.90,
    retry_attempts=5
)

# Faster (lower quality)
config = OrchestratorConfig(
    quality_threshold=0.80,
    retry_attempts=2
)
```

## Benchmarking

### Basic Benchmark

```python
import time
import asyncio
from statistics import mean, stdev

async def benchmark(orchestrator, request, iterations=10):
    latencies = []
    quality_scores = []
    
    for i in range(iterations):
        start = time.time()
        doc = await orchestrator.create_document(request)
        latency = time.time() - start
        
        latencies.append(latency)
        quality_scores.append(doc.quality_score)
    
    return {
        'avg_latency': mean(latencies),
        'std_latency': stdev(latencies),
        'avg_quality': mean(quality_scores),
        'throughput': 3600 / mean(latencies)
    }

results = await benchmark(orchestrator, request)
print(f"Average latency: {results['avg_latency']:.2f}s")
print(f"Throughput: {results['throughput']:.1f} docs/hour")
print(f"Quality: {results['avg_quality']:.2%}")
```

### Load Testing

```python
async def load_test(orchestrator, num_concurrent=10):
    requests = [create_request() for _ in range(num_concurrent)]
    
    start = time.time()
    documents = await asyncio.gather(*[
        orchestrator.create_document(req)
        for req in requests
    ])
    duration = time.time() - start
    
    return {
        'total_time': duration,
        'avg_time_per_doc': duration / num_concurrent,
        'successful': len([d for d in documents if d.status == DocumentStatus.COMPLETE])
    }
```

## Cost Optimization

### Token Cost Tracking

```python
class CostTracker:
    # Pricing per 1K tokens (example rates)
    COSTS = {
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002}
    }
    
    def calculate_cost(self, model, input_tokens, output_tokens):
        costs = self.COSTS.get(model, self.COSTS['gpt-4'])
        return (
            (input_tokens / 1000) * costs['input'] +
            (output_tokens / 1000) * costs['output']
        )
```

### Cost-Effective Configuration

```python
# Use cheaper models where appropriate
config = OrchestratorConfig(
    research_config=AgentConfig(
        model_config=ModelConfig(model="gpt-4")  # Need accuracy
    ),
    writing_config=AgentConfig(
        model_config=ModelConfig(model="gpt-4")  # Need quality
    ),
    editing_config=AgentConfig(
        model_config=ModelConfig(model="gpt-3.5-turbo")  # Can be cheaper
    ),
    verification_config=AgentConfig(
        model_config=ModelConfig(model="gpt-4")  # Need accuracy
    )
)
```

## Scaling

### Horizontal Scaling

**Multiple orchestrator instances:**

```python
# Deploy multiple instances
instances = [
    DocumentOrchestrator(config)
    for _ in range(num_instances)
]

# Load balance requests
async def load_balanced_create(request):
    # Simple round-robin
    orchestrator = instances[current_index % len(instances)]
    return await orchestrator.create_document(request)
```

### Vertical Scaling

**Increase resources per instance:**

```python
config = OrchestratorConfig(
    max_agents=50,  # More agents
    max_concurrent_tasks=20  # More parallelism
)
```

## Monitoring

### Performance Dashboard

```python
import logging
import time
from collections import deque

class PerformanceMonitor:
    def __init__(self, window_size=100):
        self.latencies = deque(maxlen=window_size)
        self.quality_scores = deque(maxlen=window_size)
        self.start_time = time.time()
        self.total_documents = 0
    
    def record_document(self, document, latency):
        self.latencies.append(latency)
        self.quality_scores.append(document.quality_score)
        self.total_documents += 1
    
    def get_stats(self):
        return {
            'avg_latency': mean(self.latencies) if self.latencies else 0,
            'avg_quality': mean(self.quality_scores) if self.quality_scores else 0,
            'total_documents': self.total_documents,
            'uptime': time.time() - self.start_time,
            'throughput': self.total_documents / (time.time() - self.start_time) * 3600
        }
```

## Best Practices

1. **Start with defaults** and optimize based on measurements
2. **Monitor continuously** to identify bottlenecks
3. **Test at scale** before production deployment
4. **Balance cost vs. performance** based on requirements
5. **Use caching** for repeated operations
6. **Optimize prompts** to reduce token usage
7. **Scale horizontally** for high throughput
8. **Set appropriate timeouts** to prevent hanging
9. **Track costs** to manage budget
10. **Profile regularly** to find optimization opportunities

## Troubleshooting

### Slow Performance

1. Check agent utilization
2. Verify API response times
3. Review timeout settings
4. Check for bottlenecks in sequential stages
5. Increase parallelism if underutilized

### High Costs

1. Review token usage
2. Consider cheaper models
3. Implement caching
4. Optimize prompts
5. Reduce max_tokens where appropriate

### Low Quality

1. Increase quality threshold
2. Use better models
3. Enable more verification steps
4. Increase retry attempts
5. Review and improve prompts

---

**See Also**:
- [Architecture](architecture.md)
- [Configuration Guide](configuration.md)
- [API Reference](api_reference.md)