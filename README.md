# Multi-Agent Document Framework

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production-ready framework for building sophisticated multi-agent document creation systems. This framework enables you to orchestrate multiple specialized AI agents that collaborate to create, verify, and refine complex documents.

## 🌟 Key Features

- **Multi-Agent Orchestration**: Coordinate multiple specialized agents with different roles and expertise
- **Content Verification**: Built-in verification system to ensure quality and consistency
- **Flexible Architecture**: Easily extensible for custom agent types and workflows
- **Role-Based Agents**: Specialized agents for research, writing, editing, fact-checking, and more
- **Document Assembly**: Intelligent document composition from multiple agent contributions
- **Async Support**: Built for high-performance concurrent agent operations
- **Comprehensive Logging**: Track agent activities and decision-making processes
- **Configuration Management**: YAML-based configuration for easy customization

## 🏗️ Architecture

The framework consists of four core components:

1. **Agents**: Specialized units that perform specific tasks (research, writing, editing, etc.)
2. **Coordinator**: Orchestrates agent collaboration and manages workflow
3. **Verification System**: Validates content quality, consistency, and accuracy
4. **Document Manager**: Assembles and manages document structure and content

```
┌─────────────────────────────────────────────────────────┐
│                     Coordinator                          │
│  (Orchestrates workflow and agent communication)        │
└──────────────┬──────────────────────────┬───────────────┘
               │                          │
     ┌─────────▼─────────┐      ┌────────▼──────────┐
     │   Agent Pool      │      │  Verification     │
     │                   │      │     System        │
     │ • Research Agent  │      │                   │
     │ • Writer Agent    │◄─────┤ • Quality Check   │
     │ • Editor Agent    │      │ • Fact Check      │
     │ • Fact-Checker    │      │ • Consistency     │
     └─────────┬─────────┘      └───────────────────┘
               │
     ┌─────────▼─────────┐
     │ Document Manager  │
     │  (Assembly &      │
     │   Structure)      │
     └───────────────────┘
```

## 📦 Installation

### From Source

```bash
git clone https://github.com/andrexibiza/multi-agent-document-framework.git
cd multi-agent-document-framework
pip install -e .
```

### Using pip (when published)

```bash
pip install multi-agent-document-framework
```

### Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## 🚀 Quick Start

### Simple Document Creation

```python
from multi_agent_framework import Agent, Coordinator, DocumentManager
from multi_agent_framework.config import Config

# Initialize configuration
config = Config.from_yaml('config.yaml')

# Create specialized agents
researcher = Agent(
    agent_id="researcher_01",
    role="researcher",
    capabilities=["web_search", "data_analysis"],
    model="gpt-4"
)

writer = Agent(
    agent_id="writer_01",
    role="writer",
    capabilities=["content_creation", "storytelling"],
    model="gpt-4"
)

editor = Agent(
    agent_id="editor_01",
    role="editor",
    capabilities=["proofreading", "style_improvement"],
    model="gpt-4"
)

# Initialize coordinator
coordinator = Coordinator(
    agents=[researcher, writer, editor],
    config=config
)

# Create document
document = coordinator.create_document(
    topic="The Future of Artificial Intelligence",
    requirements={
        "length": "2000 words",
        "style": "technical but accessible",
        "sections": ["Introduction", "Current State", "Future Trends", "Conclusion"]
    }
)

print(document.content)
```

### Advanced Multi-Agent Workflow

```python
import asyncio
from multi_agent_framework import Coordinator, Agent
from multi_agent_framework.verification import VerificationSystem

async def create_research_paper():
    # Create agent team
    agents = [
        Agent("researcher_01", "researcher", ["literature_review", "data_collection"]),
        Agent("analyst_01", "analyst", ["data_analysis", "statistical_modeling"]),
        Agent("writer_01", "writer", ["academic_writing", "technical_writing"]),
        Agent("reviewer_01", "reviewer", ["peer_review", "methodology_check"]),
        Agent("editor_01", "editor", ["formatting", "citation_management"])
    ]
    
    # Setup verification
    verification = VerificationSystem(
        checks=["factual_accuracy", "consistency", "completeness", "citations"]
    )
    
    # Initialize coordinator with verification
    coordinator = Coordinator(
        agents=agents,
        verification_system=verification,
        max_iterations=5
    )
    
    # Create document with iterative refinement
    document = await coordinator.create_document_async(
        topic="Multi-Agent Systems in Document Generation",
        requirements={
            "type": "research_paper",
            "length": "8000 words",
            "citation_style": "IEEE",
            "sections": [
                "Abstract",
                "Introduction",
                "Literature Review",
                "Methodology",
                "Results",
                "Discussion",
                "Conclusion",
                "References"
            ]
        }
    )
    
    return document

# Run the workflow
document = asyncio.run(create_research_paper())
print(f"Document created with {document.word_count} words")
print(f"Verification score: {document.verification_score}")
```

## 📚 Documentation

- **[Architecture Guide](docs/architecture.md)**: Deep dive into framework architecture
- **[API Reference](docs/api_reference.md)**: Complete API documentation
- **[Agent Design](docs/agent_design.md)**: How to create custom agents
- **[Workflows](docs/workflows.md)**: Common workflow patterns and best practices

## 🔧 Configuration

Create a `config.yaml` file:

```yaml
framework:
  name: "Multi-Agent Document Framework"
  version: "1.0.0"

agents:
  default_model: "gpt-4"
  timeout: 300
  max_retries: 3

coordinator:
  max_concurrent_agents: 5
  collaboration_mode: "sequential"  # or "parallel"
  enable_feedback_loops: true

verification:
  enabled: true
  min_quality_score: 0.8
  checks:
    - factual_accuracy
    - consistency
    - completeness
    - grammar
    - style

document:
  default_format: "markdown"
  auto_save: true
  versioning: true

logging:
  level: "INFO"
  file: "logs/framework.log"
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

With coverage:

```bash
pytest --cov=multi_agent_framework tests/
```

## 📖 Examples

Check the `examples/` directory for:

- `simple_document.py`: Basic document creation
- `multi_agent_document.py`: Advanced multi-agent collaboration
- `custom_agent.py`: Creating custom agent types
- `verification_pipeline.py`: Setting up verification workflows

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by modern multi-agent AI research
- Built with best practices from software engineering and AI communities
- Thanks to all contributors and users

## 📞 Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/andrexibiza/multi-agent-document-framework/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/andrexibiza/multi-agent-document-framework/discussions)

## 🗺️ Roadmap

- [ ] Support for more LLM providers (Claude, Gemini, etc.)
- [ ] Visual workflow designer
- [ ] Real-time collaboration features
- [ ] Template library for common document types
- [ ] Integration with document management systems
- [ ] Advanced analytics and reporting
- [ ] Multi-language support

---

**Built with ❤️ by the Multi-Agent Framework Team**