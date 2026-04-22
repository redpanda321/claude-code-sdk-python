# claude-code-sdk

Python SDK port of [claude-code](https://github.com/redpanda321/claude-code) (CCB) --
a library-first, CLI-free Claude Code agent toolkit.

**Status:** Alpha. Public API is unstable.

This is the Python sibling of
[`claude-code-sdk-ts`](https://github.com/redpanda321/claude-code-sdk-ts).
Public API parity with the TypeScript distribution is a non-goal only where
Python idioms demand otherwise (async via `asyncio`, Pydantic v2 for schemas,
`typing.Protocol` for the `Tool` contract).

## Install

```bash
pip install claude-code-sdk       # not yet published -- v0.1.0a1 planned
```

Optional extras:

```bash
pip install "claude-code-sdk[agent-sdk]"   # enables Anthropic claude-agent-sdk adapter
pip install "claude-code-sdk[dev]"         # test + lint + typecheck toolchain
```

## Scope

This package ships **the SDK only**. There is no CLI/TUI -- `claude-code-sdk`
is a library. CLI tooling lives in a separate repository.

Subpackages (placeholders shipped in v0.1.0a1, populated over follow-up releases):

- `adapters` -- `claude_agent_sdk` bidirectional bridge (populated in v0.1.0a1)
- `tools` -- `Tool[Input, Output, Progress]` Protocol + tool registry
- `mcp` -- Model Context Protocol client
- `providers` -- model-provider abstractions
- `hooks`, `plugins`, `skills`, `commands` -- agent extension points
- `memdir`, `subagents`, `permissions`, `compaction` -- runtime services

## Requirements

- Python 3.11+ (ExceptionGroup, tomllib)
- See `pyproject.toml` for runtime deps.

## License

MIT. See [LICENSE](LICENSE).
