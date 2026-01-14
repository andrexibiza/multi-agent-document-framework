# Contributing to Multi-Agent Document Framework

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/andrexibiza/multi-agent-document-framework.git
cd multi-agent-document-framework
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Install Development Tools

```bash
pip install pytest pytest-asyncio pytest-cov black flake8 mypy
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number-description
```

### 2. Make Changes

- Write clear, documented code
- Follow existing code style
- Add tests for new features
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=madf --cov-report=html

# Run specific test
pytest tests/test_orchestrator.py::test_create_document
```

### 4. Code Quality Checks

```bash
# Format code
black src/

# Check style
flake8 src/

# Type checking
mypy src/
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature" # or "fix:", "docs:", etc.
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Contribution Guidelines

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for all public functions/classes
- Keep functions focused and small
- Use meaningful variable names

### Documentation

- Update README.md if adding features
- Add docstrings to new code
- Update relevant documentation files
- Include examples for new features

### Testing

- Write tests for new features
- Maintain test coverage above 80%
- Test edge cases and error conditions
- Use async test fixtures appropriately

### Pull Request Process

1. **Description**: Provide clear description of changes
2. **Tests**: Ensure all tests pass
3. **Documentation**: Update docs as needed
4. **Review**: Address review comments
5. **Merge**: Maintainer will merge once approved

## What to Contribute

### Good First Issues

- Documentation improvements
- Additional examples
- Test coverage improvements
- Bug fixes
- Performance optimizations

### Feature Requests

- New agent types
- Additional workflow patterns
- Integration with new LLM providers
- Enhanced quality metrics
- Visualization tools

### Bug Reports

When reporting bugs, include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- System information
- Minimal code example

## Project Structure

```
multi-agent-document-framework/
├── src/madf/           # Main source code
│   ├── agents/         # Agent implementations
│   ├── coordination/   # Coordination layer
│   ├── models/         # Data models
│   ├── utils/          # Utilities
│   └── storage/        # Storage layer
├── tests/              # Test suite
├── docs/               # Documentation
├── examples/           # Example scripts
└── config/             # Configuration files
```

## Development Tips

### Running Examples

```bash
# Set API key
export OPENAI_API_KEY="your-key-here"

# Run example
python examples/basic_document.py
```

### Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use breakpoints
import pdb; pdb.set_trace()
```

### Testing Async Code

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

## Questions?

If you have questions:
- Open an issue on GitHub
- Check existing documentation
- Review closed issues for similar questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the Multi-Agent Document Framework!