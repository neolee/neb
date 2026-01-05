# AGENTS.md

## Build/Lint/Test Commands

```bash
# Run Python scripts
uv run <script_name>.py

# Linting (use ruff)
uv run ruff check .                    # Check for lint issues
uv run ruff check . --fix               # Auto-fix lint issues
uv run ruff check <file.py>             # Lint specific file

# Format (ruff also handles formatting)
uv run ruff format .                    # Format all files
uv run ruff format <file.py>            # Format specific file

# Type checking (basedpyright language server)
# Note: basedpyright is configured as LSP, not run via CLI
# Use your IDE/editor LSP integration for type checking

# Run single examples
uv run hello.py                         # Run hello world example
uv run pydantic_model.py                # Run Pydantic model example
uv run kb_online.py build|search        # Build or search with online RAG
uv run kb_local.py <query>              # Search with local PDF RAG
```

## Code Style Guidelines

### Imports
- Standard library → Third-party → Local modules
- Use `from __future__ import annotations as _annotations` at the top of async files
- Group imports logically with blank lines between groups
```python
from __future__ import annotations as _annotations

import asyncio
from dataclasses import dataclass

import httpx
from pydantic_ai import Agent

import models as m
from mal.adapter.openai import Embedder
```

### Type Hints
- Use modern Python 3.11+ syntax: `list[str]`, `dict[str, int]`, `str | None`
- Never use `typing.List`, `typing.Dict`, `typing.Optional`
- Use `str | None` instead of `Optional[str]`
- Always type function parameters and return values in agent code

### Naming Conventions
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `ALL_CAPS`
- Private members: `_leading_underscore`
- Agent instances: `<name>_agent` (e.g., `weather_agent`, `rag_agent`)
- Dependencies dataclass: `Deps` or `<Name>Deps`

### Error Handling
- HTTP calls: use `response.raise_for_status()` after requests
- Expected errors: raise `ValueError` with descriptive messages
- Agent retries: use `ModelRetry` exception for retryable errors
- Database: raise `ValueError` for not found or invalid data
- API keys: check `os.getenv()` returns non-None value before use

### Async Patterns
- Always use `async with` for context managers (AsyncClient, asyncpg pools)
- Use `asyncio.run()` in `if __name__ == "__main__":` blocks
- Use `@asynccontextmanager` for resource management
- Use `async with agent:` for agent lifecycle management
- Use `Semaphore` and `TaskGroup` for concurrency control

### Pydantic-AI Patterns
- Use `@dataclass` for dependencies passed to `deps_type`
- Register tools with `@agent.tool` decorator
- Tool functions: `async def tool_name(ctx: RunContext[Deps], param: type) -> return_type:`
- Use `Agent` with proper `model`, `deps_type`, and `output_type`
- Use `@agent.system_prompt` decorator for dynamic system prompts
- Use `result.output` to access agent outputs
- Use `result.usage()` to check token usage
- For streaming: `async with agent.run_stream(prompt) as result:` then `async for chunk in result.stream_text():`

### Data Structures
- Use `@dataclass` for simple data containers
- Use `pydantic.BaseModel` for data validation and structured outputs
- Use `pydantic.Field(description="...")` for field descriptions
- Use `pydantic_ai.format_as_xml()` for XML formatting of data

### Logging/Observability
- Import `instrument` module and call `instrument.init()` at module level
- Use `logfire.info()` for informational messages with structured data: `logfire.info("message", key=value)`
- Use `logfire.span("context description")` for operation tracing
- Use `span.set_attribute("key", value)` to add context to spans

### Database/Vector Store Patterns
- Use connection pooling with `asyncpg.create_pool()`
- Use parameterized queries with `$1`, `$2` syntax
- Implement RAGStore abstract base class for vector stores
- Store embeddings as JSON using `pydantic_core.to_json(embedding).decode()`

### Testing
- Currently no test framework configured
- When adding tests, prefer pytest with async support
- Test files should be named `test_*.py` or `*_test.py`

### Code Comments
- DO NOT add comments unless explicitly requested
- Use docstrings only for public APIs and complex functions
- Keep code self-documenting through clear naming

### MAL (Model Abstraction Layer)
- Import models with `import models as m` pattern
- Use `m.default` for the default model, or specific models like `m.deepseek`
- Access embedders from `embedders.py` (e.g., `nomic`, `snowflake`)
- Use `openai_model("provider/model")` for OpenAI-compatible models
- Provider configurations are in `providers.toml`

### File Organization
- Agent examples: root directory (`hello.py`, `weather.py`, etc.)
- RAG framework: `rag/` subdirectory
- MAL abstraction: `mal/` subdirectory
- Utilities: `util/` subdirectory
- Reference documentation: `ref/` subdirectory
