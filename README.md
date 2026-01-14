# Multi-Agent Document Framework

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production-ready framework for building multi-agent document creation systems with intelligent coordination, verification, and quality control.

## 🎯 Overview

The Multi-Agent Document Framework enables the creation of sophisticated document generation systems using specialized AI agents that work together through coordinated workflows. Each agent has a specific role (research, writing, editing, verification) and the system orchestrates their collaboration to produce high-quality documents.

### Key Features

- **🤖 Multi-Agent Orchestration**: Coordinate multiple specialized agents with different capabilities
- **📝 Document Pipeline**: Complete workflow from research to final output
- **✅ Quality Assurance**: Built-in verification and validation systems
- **🔄 Error Recovery**: Robust error handling and retry mechanisms
- **🎨 Flexible Architecture**: Extensible design for custom agents and workflows
- **📊 Performance Monitoring**: Track agent performance and system metrics
- **🔌 LLM Agnostic**: Works with OpenAI, Anthropic, local models, and more

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Orchestrator                            │
│  (Coordinates agents, manages workflow, handles routing)    │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        │            │            │            │
   ┌────▼───┐  ┌────▼───┐  ┌────▼───┐  ┌────▼───┐
   │Research│  │Writing │  │Editing │  │Verify  │
   │ Agent  │  │ Agent  │  │ Agent  │  │ Agent  │
   └────┬───┘  └────┬───┘  └────┬───┘  └────┬───┘
        │            │            │            │
        └────────────┴────────────┴────────────┘
                     │
            ┌────────▼─────────┐
            │  Document Store  │
            │  Version Control │
            └──────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/andrexibiza/multi-agent-document-framework.git
cd multi-agent-document-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Basic Usage

```python
from madf import DocumentOrchestrator, ResearchAgent, WritingAgent, EditingAgent, VerificationAgent
from madf.config import OrchestratorConfig

# Initialize agents
research_agent = ResearchAgent(model="gpt-4")
writing_agent = WritingAgent(model="gpt-4")
editing_agent = EditingAgent(model="gpt-4")
verification_agent = VerificationAgent(model="gpt-4")

# Create orchestrator
config = OrchestratorConfig(
    max_iterations=3,
    quality_threshold=0.85,
    enable_verification=True
)

orchestrator = DocumentOrchestrator(
    agents={
        'research': research_agent,
        'writing': writing_agent,
        'editing': editing_agent,
        'verification': verification_agent
    },
    config=config
)

# Generate document
result = orchestrator.create_document(
    topic="The Impact of Artificial Intelligence on Healthcare",
    requirements={
        "length": "2000-3000 words",
        "tone": "professional",
        "include_citations": True,
        "target_audience": "healthcare professionals"
    }
)

print(f"Document created: {result.document_id}")
print(f"Quality score: {result.quality_score}")
print(f"\nContent:\n{result.content}")
```

## 📚 Documentation

- [Technical Architecture](docs/architecture.md) - System design and components
- [Agent Design](docs/agents.md) - Agent roles and capabilities
- [Coordination Protocol](docs/coordination.md) - How agents communicate
- [Verification System](docs/verification.md) - Quality control mechanisms
- [API Reference](docs/api_reference.md) - Complete API documentation
- [Configuration Guide](docs/configuration.md) - Setup and customization
- [Examples](examples/) - Real-world usage examples

## 🎓 How It Works

### The Multi-Agent Workflow

1. **Request Analysis**: The orchestrator analyzes the document request and determines the required workflow
2. **Research Phase**: Research agent gathers information, sources, and context
3. **Writing Phase**: Writing agent creates initial draft based on research
4. **Editing Phase**: Editing agent refines content, improves clarity, checks consistency
5. **Verification Phase**: Verification agent validates accuracy, completeness, and quality
6. **Iteration**: If quality threshold not met, cycle repeats with feedback
7. **Finalization**: Document is finalized and returned with metadata

### Why Multi-Agent?

**Specialization**: Each agent is optimized for a specific task, leading to better results than a single general-purpose agent.

**Parallel Processing**: Multiple agents can work simultaneously on different aspects of the document.

**Quality Control**: Dedicated verification agents ensure high-quality output through systematic checks.

**Scalability**: Add new specialized agents without modifying existing ones.

**Fault Tolerance**: If one agent fails, others can continue or compensate.

## 🔧 Advanced Features

### Custom Agents

Create your own specialized agents:

```python
from madf.agents import BaseAgent

class CitationAgent(BaseAgent):
    def __init__(self, model="gpt-4"):
        super().__init__(name="citation", model=model)
    
    def process(self, context):
        # Custom citation logic
        return self.generate_citations(context)
```

### Workflow Customization

```python
from madf.workflows import WorkflowBuilder

# Build custom workflow
workflow = WorkflowBuilder() \
    .add_stage("research", parallel=True) \
    .add_stage("outline") \
    .add_stage("writing", parallel=True, chunks=5) \
    .add_stage("editing") \
    .add_stage("verification") \
    .add_condition("quality_check", threshold=0.9) \
    .add_loop(max_iterations=3) \
    .build()

orchestrator.set_workflow(workflow)
```

### Monitoring and Analytics

```python
from madf.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()
orchestrator.add_monitor(monitor)

# After document generation
metrics = monitor.get_metrics()
print(f"Total time: {metrics.total_time}")
print(f"Agent breakdown: {metrics.agent_times}")
print(f"Token usage: {metrics.token_usage}")
```

## 📊 Project Structure

```
multi-agent-document-framework/
├── src/madf/
│   ├── __init__.py
│   ├── orchestrator.py          # Main orchestration logic
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py              # Base agent class
│   │   ├── research.py          # Research agent
│   │   ├── writing.py           # Writing agent
│   │   ├── editing.py           # Editing agent
│   │   └── verification.py      # Verification agent
│   ├── coordination/
│   │   ├── __init__.py
│   │   ├── protocol.py          # Communication protocol
│   │   ├── message_bus.py       # Message passing system
│   │   └── state_manager.py     # Shared state management
│   ├── verification/
│   │   ├── __init__.py
│   │   ├── quality_checker.py   # Quality assessment
│   │   ├── fact_checker.py      # Fact verification
│   │   └── consistency.py       # Consistency checks
│   ├── workflows/
│   │   ├── __init__.py
│   │   ├── builder.py           # Workflow construction
│   │   └── executor.py          # Workflow execution
│   ├── models/
│   │   ├── __init__.py
│   │   ├── document.py          # Document model
│   │   └── context.py           # Context model
│   └── utils/
│       ├── __init__.py
│       ├── llm_wrapper.py       # LLM abstraction
│       └── prompts.py           # Prompt templates
├── docs/
│   ├── architecture.md
│   ├── agents.md
│   ├── coordination.md
│   ├── verification.md
│   ├── api_reference.md
│   └── configuration.md
├── examples/
│   ├── basic_usage.py
│   ├── custom_agents.py
│   ├── advanced_workflow.py
│   └── monitoring_example.py
├── tests/
│   ├── test_orchestrator.py
│   ├── test_agents.py
│   ├── test_coordination.py
│   └── test_verification.py
├── config/
│   ├── default_config.yaml
│   └── agent_configs/
├── requirements.txt
├── setup.py
├── pyproject.toml
└── README.md
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=madf tests/

# Run specific test
pytest tests/test_orchestrator.py
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by multi-agent AI research and Claude's workflow design patterns
- Built on top of modern LLM capabilities and agentic frameworks

## 📞 Contact

For questions or support, please open an issue or contact the maintainers.

---

**Note**: This framework is designed for production use but requires proper API keys and configuration. See the [Configuration Guide](docs/configuration.md) for setup instructions.