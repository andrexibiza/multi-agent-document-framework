# Contributing to Multi-Agent Document Framework

Thank you for your interest in contributing to the Multi-Agent Document Framework! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/multi-agent-document-framework.git
   cd multi-agent-document-framework
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/andrexibiza/multi-agent-document-framework.git
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip or conda for package management
- Git

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks (optional but recommended):
   ```bash
   pre-commit install
   ```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior**
- **Actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Code samples** or test cases if applicable

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Clear title and description**
- **Use case** or motivation
- **Proposed solution** or implementation approach
- **Alternatives considered**

### Code Contributions

1. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Add tests** for new functionality

4. **Update documentation** as needed

5. **Run tests** to ensure everything works:
   ```bash
   pytest
   ```

6. **Commit your changes** with clear messages:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Imports**: Organized using isort
- **Type hints**: Encouraged for public APIs

### Code Formatting

We use **Black** for code formatting:

```bash
black src/ tests/
```

### Linting

Run linters before committing:

```bash
flake8 src/ tests/
mypy src/
pylint src/
```

### Documentation Style

- Use **Google-style docstrings**
- Include type hints in function signatures
- Provide usage examples for complex functions
- Keep docstrings concise but informative

Example:

```python
def create_agent(
    role: str,
    capabilities: List[str],
    model: str = "gpt-4"
) -> Agent:
    """
    Create a new agent with specified role and capabilities.
    
    Args:
        role: The agent's role (e.g., "researcher", "writer")
        capabilities: List of agent capabilities
        model: LLM model to use (default: "gpt-4")
    
    Returns:
        Configured Agent instance
    
    Example:
        >>> agent = create_agent("researcher", ["web_search"])
        >>> print(agent.role)
        researcher
    """
    return Agent(role=role, capabilities=capabilities, model=model)
```

## Testing

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=multi_agent_framework --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_agent.py
```

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Use fixtures for common setup

Example:

```python
import pytest
from multi_agent_framework import Agent


class TestAgent:
    def test_agent_creation(self):
        """Test that agent is created with correct attributes."""
        # Arrange
        role = "researcher"
        capabilities = ["web_search"]
        
        # Act
        agent = Agent(role=role, capabilities=capabilities)
        
        # Assert
        assert agent.role == role
        assert agent.capabilities == capabilities
```

## Documentation

### Updating Documentation

- Update docstrings when changing function signatures
- Add examples for new features
- Update README.md for significant changes
- Add entries to docs/ for new modules or major features

### Building Documentation

If using Sphinx (future):

```bash
cd docs
make html
```

## Pull Request Process

### Before Submitting

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run full test suite**:
   ```bash
   pytest
   ```

3. **Check code quality**:
   ```bash
   black --check src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

4. **Update CHANGELOG** (if applicable)

### Pull Request Guidelines

- **Title**: Clear, concise description of changes
- **Description**: Include:
  - What changed and why
  - Related issues (use "Fixes #123" or "Relates to #123")
  - Testing performed
  - Breaking changes (if any)
  - Screenshots (if UI changes)

- **Size**: Keep PRs focused and reasonably sized
- **Commits**: Clean, logical commit history
- **Tests**: Include tests for new functionality
- **Documentation**: Update docs as needed

### Review Process

1. Automated checks must pass
2. At least one maintainer review required
3. Address review feedback
4. Maintainer will merge when ready

### After Merge

Your contribution will be included in the next release. Thank you!

## Development Workflow

### Branching Strategy

- `main`: Stable, production-ready code
- `develop`: Integration branch for features (if used)
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `docs/*`: Documentation updates
- `refactor/*`: Code refactoring

### Commit Messages

Follow conventional commits format:

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Example:
```
feat(agent): add support for custom LLM providers

- Add LLMProvider interface
- Implement OpenAI provider
- Add configuration for provider selection

Closes #123
```

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/andrexibiza/multi-agent-document-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/andrexibiza/multi-agent-document-framework/discussions)
- **Email**: support@example.com

## Recognition

Contributors will be recognized in:
- Release notes
- Contributors file
- Project documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the Multi-Agent Document Framework! 🎉