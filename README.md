# claude-code-sdk

[![CI](https://github.com/redpanda321/claude-code-sdk-python/actions/workflows/ci.yml/badge.svg)](https://github.com/redpanda321/claude-code-sdk-python/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://github.com/redpanda321/claude-code-sdk-python)
[![PyPI](https://img.shields.io/pypi/v/claude-code-sdk.svg)](https://pypi.org/project/claude-code-sdk/)

**Library-first, CLI-free Claude Code agent toolkit for Python.**

`claude-code-sdk` is a Python port of the Claude Code Builder (CCB) TypeScript
package at [`claude-code-sdk-ts`](https://github.com/redpanda321/claude-code-sdk-ts).
It gives you the building blocks needed to author Claude-powered agents --
tools, providers, hooks, plugins, skills, commands, MCP servers, permissions,
subagents, memory, and compaction -- without ever shelling out to a CLI.

> **Status: Alpha (pre-0.1.0a1).** The initial release ships the scaffold,
> `Tool` Protocol, a bidirectional `claude-agent-sdk` adapter, and CI. The
> other 11 public barrels (`providers`, `mcp`, `hooks`, ...) are declared but
> empty -- they drain from the TypeScript source over subsequent milestones.
> See [`ROADMAP.md`](./ROADMAP.md) for the drain sequence.

## Install

```bash
# Core
pip install claude-code-sdk

# With the claude-agent-sdk adapter (optional extra)
pip install "claude-code-sdk[agent-sdk]"
```

> The first PyPI release (`0.1.0a1`) is **held** pending Plan 06 sign-off. See
> "Release status" below.

## Quickstart: author a Tool

```python
from collections.abc import AsyncIterator

from pydantic import BaseModel
from claude_code_sdk.tools import (
    PermissionResult,
    Tool,
    ToolCallProgress,
    ToolContext,
    ToolResult,
)


class EchoInput(BaseModel):
    text: str


class EchoTool:
    name = "echo"
    description = "Echo the input text back as output."
    input_model = EchoInput
    is_read_only = True
    is_enabled = True

    def validate_input(self, raw: dict) -> EchoInput:
        return EchoInput.model_validate(raw)

    async def check_permissions(self, input, context) -> PermissionResult:
        return PermissionResult(decision="allow")

    async def can_use_tool(self, context) -> bool:
        return True

    async def call(self, input: EchoInput, context: ToolContext) -> AsyncIterator:
        yield ToolCallProgress(data={"step": "start"})
        yield ToolResult(output=input.text)

    def render_result_for_assistant(self, result: ToolResult) -> str:
        return str(result.output)


# Runtime-checkable Protocol -- conformance is structural.
assert isinstance(EchoTool(), Tool)
```

## Bridge to claude-agent-sdk

```python
from claude_code_sdk.adapters import from_agent_sdk_tool, to_agent_sdk_tool

# Expose a CCB-native Tool to Anthropic's SdkMcpTool registry.
sdk_tool = to_agent_sdk_tool(EchoTool())
assert sdk_tool.name == "echo"

# ...or wrap an SdkMcpTool so CCB consumers can call it through Tool Protocol.
wrapped = from_agent_sdk_tool(sdk_tool)
assert wrapped.name == "echo"
```

The adapter is bidirectional, lazy-imports `claude_agent_sdk` only in the
`to_` direction, and is fully unit-tested.

## Public surface (v1)

`claude_code_sdk` exports 12 subpackages. In v1 only `tools`, `adapters`, and
`__init__.__version__` are populated. The other 11 are declared with empty
`__all__` and a CCB-drain-source docstring naming the TypeScript module each
will mirror:

| Barrel | Status | Ports from (TS) |
|--------|--------|-----------------|
| `tools` | partial | `claude-code-sdk-ts/src/tools` |
| `adapters` | populated | `claude-code-sdk-ts/src/adapters` |
| `mcp` | placeholder | `claude-code-sdk-ts/src/mcp` |
| `providers` | placeholder | `claude-code-sdk-ts/src/providers` |
| `hooks` | placeholder | `claude-code-sdk-ts/src/hooks` |
| `plugins` | placeholder | `claude-code-sdk-ts/src/plugins` |
| `skills` | placeholder | `claude-code-sdk-ts/src/skills` |
| `commands` | placeholder | `claude-code-sdk-ts/src/commands` |
| `memdir` | placeholder | `claude-code-sdk-ts/src/memdir` |
| `subagents` | placeholder | `claude-code-sdk-ts/src/subagents` |
| `permissions` | placeholder | `claude-code-sdk-ts/src/permissions` |
| `compaction` | placeholder | `claude-code-sdk-ts/src/compaction` |

## Release status

`0.1.0a1` is held pending Plan 06 sign-off. Maintainers trigger publication
manually:

```bash
git tag v0.1.0a1
git push origin v0.1.0a1
# or
gh workflow run Release --ref main -f dry-run=false
```

Publishing uses PyPI **trusted publishing** (OIDC via `pypa/gh-action-pypi-publish`);
the `pypi` GitHub Environment must be configured out-of-band on first release.

## Design goals

- **No `console_scripts`**: this is a library. CLI/TUI lives in a separate repo.
- **`src/`-layout**, PEP 621, hatchling + hatch-vcs versioning.
- **Strict typing**: `py.typed` marker; pyright strict mode in CI (soft-fail
  during alpha carve-in).
- **Minimal runtime deps**: `anyio`, `httpx`, `pydantic`, `mcp`.

## Links

- [ROADMAP.md](./ROADMAP.md) -- drain sequence from CCB TypeScript.
- [CHANGELOG.md](./CHANGELOG.md) -- release history.
- [CONTRIBUTING.md](./CONTRIBUTING.md) -- dev setup, test loop, commit style.
- [SECURITY.md](./SECURITY.md) -- responsible disclosure.
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) -- Contributor Covenant 2.1.
- Sibling: [`claude-code-sdk-ts`](https://github.com/redpanda321/claude-code-sdk-ts) (TypeScript v1 source).

## License

MIT. See [`LICENSE`](./LICENSE).
