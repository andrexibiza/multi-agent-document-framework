# Configuration Guide

## Overview

The Multi-Agent Document Framework uses a hierarchical configuration system that allows you to customize behavior at multiple levels.

## Configuration Levels

```
Default Config ← File Config ← Environment Variables ← Runtime Config
   (Lowest priority)                                   (Highest priority)
```

## Configuration Files

### YAML Configuration

**Location**: `config/default.yaml`, `config/production.yaml`, etc.

```yaml
orchestrator:
  max_agents: 10
  timeout: 300
  quality_threshold: 0.85
  enable_parallel: true
  max_concurrent_tasks: 5
  retry_attempts: 3

agents:
  research:
    provider: "openai"
    model: "gpt-4"
    temperature: 0.3
    max_tokens: 4000
    timeout: 120
    max_retries: 3
    cache_enabled: true
  
  writing:
    provider: "openai"
    model: "gpt-4"
    temperature: 0.7
    max_tokens: 8000
    timeout: 180
    max_retries: 3
    cache_enabled: true
  
  editing:
    provider: "openai"
    model: "gpt-4"
    temperature: 0.5
    max_tokens: 8000
    timeout: 120
    max_retries: 3
    cache_enabled: true
  
  verification:
    provider: "openai"
    model: "gpt-4"
    temperature: 0.2
    max_tokens: 4000
    timeout: 120
    max_retries: 3
    cache_enabled: true

quality:
  min_score: 0.80
  verification_depth: "comprehensive"
  fact_check: true
  require_sources: false

logging:
  level: "INFO"
  file: "logs/madf.log"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Loading Configuration

```python
from madf import OrchestratorConfig

# Load from YAML file
config = OrchestratorConfig.from_yaml("config/production.yaml")

orchestrator = DocumentOrchestrator(config)
```

## Environment Variables

### API Keys

```bash
# Required
export OPENAI_API_KEY="your-key-here"

# Optional (for other providers)
export ANTHROPIC_API_KEY="your-key-here"
export COHERE_API_KEY="your-key-here"
```

### Application Settings

```bash
# Environment
export MADF_ENV=production

# Logging
export MADF_LOG_LEVEL=INFO

# Paths
export MADF_CONFIG_PATH=config/production.yaml
export MADF_STATE_PATH=./.madf_state
export MADF_OUTPUT_PATH=./output

# Performance
export MADF_MAX_AGENTS=20
export MADF_ENABLE_CACHE=true
```

### Using .env Files

```bash
# Copy example file
cp .env.example .env

# Edit with your settings
vim .env
```

```python
# Load in Python
from dotenv import load_dotenv
load_dotenv()

import os
api_key = os.getenv("OPENAI_API_KEY")
```

## Runtime Configuration

### Programmatic Configuration

```python
from madf import OrchestratorConfig, AgentConfig, ModelConfig

# Create model configurations
research_model = ModelConfig(
    provider="openai",
    model="gpt-4",
    temperature=0.3,
    max_tokens=4000
)

writing_model = ModelConfig(
    provider="openai",
    model="gpt-4",
    temperature=0.7,
    max_tokens=8000
)

# Create agent configurations
research_config = AgentConfig(
    name="research",
    model_config=research_model,
    timeout=120,
    max_retries=3
)

writing_config = AgentConfig(
    name="writing",
    model_config=writing_model,
    timeout=180,
    max_retries=3
)

# Create orchestrator configuration
config = OrchestratorConfig(
    max_agents=15,
    timeout=400,
    quality_threshold=0.88,
    enable_parallel=True,
    max_concurrent_tasks=8,
    retry_attempts=4,
    research_config=research_config,
    writing_config=writing_config
)

orchestrator = DocumentOrchestrator(config)
```

## Configuration Options

### Orchestrator Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_agents` | int | 10 | Maximum concurrent agents |
| `timeout` | int | 300 | Overall timeout (seconds) |
| `quality_threshold` | float | 0.85 | Minimum quality score (0-1) |
| `enable_parallel` | bool | true | Enable parallel processing |
| `max_concurrent_tasks` | int | 5 | Maximum concurrent tasks |
| `retry_attempts` | int | 3 | Number of retry attempts |

### Agent Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | str | - | Agent name |
| `provider` | str | "openai" | LLM provider |
| `model` | str | "gpt-4" | Model name |
| `temperature` | float | 0.7 | Sampling temperature (0-1) |
| `max_tokens` | int | 4000 | Maximum tokens to generate |
| `timeout` | int | 120 | Agent timeout (seconds) |
| `max_retries` | int | 3 | Maximum retry attempts |
| `cache_enabled` | bool | true | Enable response caching |

### Quality Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `min_score` | float | 0.80 | Minimum acceptable score |
| `verification_depth` | str | "comprehensive" | Verification level |
| `fact_check` | bool | true | Enable fact checking |
| `require_sources` | bool | false | Require source citations |

## Configuration Profiles

### Development Profile

```yaml
orchestrator:
  max_agents: 5
  timeout: 180
  quality_threshold: 0.80

agents:
  research:
    model: "gpt-3.5-turbo"  # Cheaper for dev
  writing:
    model: "gpt-3.5-turbo"
```

### Production Profile

```yaml
orchestrator:
  max_agents: 20
  timeout: 600
  quality_threshold: 0.90

agents:
  research:
    model: "gpt-4-turbo"  # Best quality
  writing:
    model: "gpt-4-turbo"
```

### Cost-Optimized Profile

```yaml
orchestrator:
  max_agents: 8
  timeout: 300
  quality_threshold: 0.85

agents:
  research:
    model: "gpt-4"
  writing:
    model: "gpt-4"
  editing:
    model: "gpt-3.5-turbo"  # Cheaper
  verification:
    model: "gpt-4"
```

## Temperature Guidelines

### By Agent Type

- **Research**: 0.2-0.4 (Low - factual accuracy)
- **Writing**: 0.6-0.8 (High - creativity)
- **Editing**: 0.4-0.6 (Medium - balanced)
- **Verification**: 0.1-0.3 (Very low - objectivity)

### By Document Type

**Academic Papers**:
```yaml
temperatures:
  research: 0.2
  writing: 0.5
  editing: 0.4
  verification: 0.2
```

**Creative Content**:
```yaml
temperatures:
  research: 0.4
  writing: 0.8
  editing: 0.6
  verification: 0.3
```

**Technical Documentation**:
```yaml
temperatures:
  research: 0.3
  writing: 0.6
  editing: 0.5
  verification: 0.2
```

## Model Selection

### OpenAI Models

| Model | Best For | Cost | Speed |
|-------|----------|------|-------|
| gpt-4-turbo | Quality | $$$ | Medium |
| gpt-4 | Balanced | $$$ | Medium |
| gpt-3.5-turbo | Speed/Cost | $ | Fast |

### Anthropic Models

| Model | Best For | Cost | Speed |
|-------|----------|------|-------|
| claude-3-opus | Highest quality | $$$$ | Slow |
| claude-3-sonnet | Balanced | $$ | Medium |
| claude-3-haiku | Speed | $ | Fast |

### Configuration Example

```yaml
agents:
  research:
    provider: "openai"
    model: "gpt-4"
  writing:
    provider: "anthropic"
    model: "claude-3-opus"
  editing:
    provider: "openai"
    model: "gpt-3.5-turbo"
  verification:
    provider: "openai"
    model: "gpt-4"
```

## Advanced Configuration

### Custom Workflows

```python
from madf.coordination import WorkflowBuilder

# Define custom workflow
custom_workflow = (WorkflowBuilder("my_workflow")
    .add_stage("research", "research")
    .add_stage("outline", "writing", depends_on=["research"])
    .add_stage("draft", "writing", depends_on=["outline"])
    .add_stage("review", "editing", depends_on=["draft"])
    .add_stage("verify", "verification", depends_on=["review"])
    .build())

# Register with orchestrator
orchestrator.workflow_manager.register_workflow("my_workflow", custom_workflow)
```

### Custom Agents

```python
from madf.agents import BaseAgent

class CustomAgent(BaseAgent):
    async def process(self, task):
        # Custom logic
        return result

# Register agent
config = AgentConfig(name="custom", model_config=model_config)
custom_agent = CustomAgent(config)
orchestrator.agents['custom'] = custom_agent
```

### Dynamic Configuration

```python
class AdaptiveConfig:
    def __init__(self, base_config):
        self.config = base_config
    
    def adjust_for_length(self, target_length):
        if target_length > 5000:
            self.config.timeout = 600
            self.config.max_agents = 20
        elif target_length > 2000:
            self.config.timeout = 400
            self.config.max_agents = 15
        else:
            self.config.timeout = 300
            self.config.max_agents = 10
        
        return self.config
```

## Configuration Validation

```python
def validate_config(config):
    """Validate configuration parameters."""
    errors = []
    
    if config.max_agents < 1:
        errors.append("max_agents must be >= 1")
    
    if not 0 <= config.quality_threshold <= 1:
        errors.append("quality_threshold must be 0-1")
    
    if config.timeout < 60:
        errors.append("timeout should be >= 60 seconds")
    
    if errors:
        raise ValueError(f"Invalid configuration: {', '.join(errors)}")
    
    return True
```

## Best Practices

1. **Start with defaults** and adjust based on needs
2. **Use environment-specific configs** (dev, staging, prod)
3. **Keep API keys in environment variables**
4. **Version control configuration files**
5. **Document custom configurations**
6. **Test configuration changes** in non-production first
7. **Monitor performance** after changes
8. **Use appropriate temperatures** for each agent type
9. **Balance cost vs. quality** based on requirements
10. **Validate configurations** before deployment

## Troubleshooting

### Configuration Not Loading

```python
# Check file exists
import os
if not os.path.exists("config/default.yaml"):
    print("Config file not found")

# Check YAML syntax
import yaml
with open("config/default.yaml") as f:
    config = yaml.safe_load(f)
    print(config)
```

### API Key Issues

```python
import os
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("OPENAI_API_KEY not set")
else:
    print(f"API key loaded: {api_key[:10]}...")
```

### Configuration Precedence

```python
# Check which config is used
config = OrchestratorConfig.from_yaml("config/default.yaml")
print(f"Max agents from file: {config.max_agents}")

# Override at runtime
config.max_agents = 20
print(f"Max agents overridden: {config.max_agents}")
```

---

**See Also**:
- [Architecture](architecture.md)
- [API Reference](api_reference.md)
- [Performance](performance.md)