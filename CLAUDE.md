# CLAUDE.md

## Build/Run Commands
- Project Management tool: `uv`
- Run application: `uv main.py`
- Install dependencies: `uv pip install -e .`
- Run tests: `pytest`
- Run single test: `pytest tests/path/to/test.py::test_function_name -v`
- Lint code: `ruff check .`
- Format code: `ruff format .`
- Type check: `mypy .`

## Code Style Guidelines
- **Formatting**: Follow PEP 8 style guide
- **Imports**: Group standard library, third-party, and local imports
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Types**: Use type hints for all function parameters and return values
- **Docstrings**: Use Google-style docstrings
- **Error Handling**: Use explicit exception handling with specific exceptions
- **Testing**: Write tests for all new functionality
- **Textual UI**: Follow Textual app conventions for UI components

# Workflow
- Be sure to typecheck when you’re done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance