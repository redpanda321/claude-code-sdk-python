# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Version strings are derived from git tags via `hatch-vcs`.

## [Unreleased]

### Added

- **Scaffold** (Plan 01): PEP 621 `pyproject.toml` using `hatchling` + `hatch-vcs`,
  `src/`-layout, `py.typed` marker, MIT license, Python >= 3.11. No `[project.scripts]`.
- **Twelve public barrels** (Plan 02): `tools`, `adapters`, `mcp`, `providers`,
  `hooks`, `plugins`, `skills`, `commands`, `memdir`, `subagents`, `permissions`,
  `compaction`. Each ships with a CCB-drain-source docstring naming the
  TypeScript sibling module it will port from. Eleven are intentionally empty
  (`__all__: list[str] = []`) pending drain in 0.2.x-0.5.x.
- **`tools.Tool` Protocol** (Plan 03): runtime-checkable `typing.Protocol`
  with generic type parameters `Input`, `Output`, `Progress`. Supporting
  frozen dataclasses: `ToolContext`, `ToolResult`, `PermissionResult`,
  `ToolCallProgress`. Six-test contract suite.
- **`adapters.claude_agent_sdk`** (Plan 04): bidirectional bridge to
  Anthropic's `claude_agent_sdk.SdkMcpTool`. `to_agent_sdk_tool()` wraps a
  CCB-native `Tool` as an `SdkMcpTool`; `from_agent_sdk_tool()` wraps any
  duck-typed `SdkMcpTool`-shaped object as a `Tool`. The `to_` direction
  requires the optional `agent-sdk` extra; the `from_` direction is
  duck-typed and needs no runtime dependency. Seven-test suite.
- **CI matrix** (Plan 05): `.github/workflows/ci.yml` runs
  `ruff check` + `ruff format --check` + `pyright` (soft-fail) + `pytest`
  on Python 3.11 / 3.12 / 3.13 using `uv`. First green run: 24806936322.
- **Docs** (Plan 06): `README.md` (quickstart, adapter demo, barrel table,
  release notes), `CONTRIBUTING.md` (uv dev loop, conventional commits,
  PR checklist forbidding `[project.scripts]`), `SECURITY.md` (7-day
  acknowledgement SLA), `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1),
  `ROADMAP.md` (0.1.x -> 1.0.0 drain sequence), this `CHANGELOG.md`.
- **Release workflow** (Plan 06): `.github/workflows/release.yml` wired for
  PyPI trusted publishing via OIDC (`pypa/gh-action-pypi-publish@release/v1`),
  triggered by `v*` tag push or manual `workflow_dispatch`. **Held**: no tag
  is pushed in this phase; first publish (`0.1.0a1`) is a separate follow-up.
- **`claude_code_sdk.mcp`** (Plan 07): `McpClient`, `mcp_client`,
  `McpServerSpec`, `McpToolRef`, `McpCallResult`, `McpTransport`. Async
  wrapper over the PyPI `mcp` package (stdio + SSE transports) with
  lazy transport imports and Pydantic v2 snake_case schemas. Ports CCB's
  MCP client surface. 12-test contract suite.
- **`claude_code_sdk.hooks`** (Plan 09): `HookRegistry`, `HookNotFoundError`,
  `HookEvent`, `HookPayload`, `HookDecision`, `HookHandler`. Seven
  lifecycle events (`pre_tool_use`, `post_tool_use`, `user_prompt_submit`,
  `session_start`, `session_end`, `stop`, `notification`); concurrent
  `asyncio.gather` dispatch with first-`block` short-circuit and
  last-write-wins `modify` merge. Ports CCB `src/utils/hooks/**`. 12-test
  suite.
- **`claude_code_sdk.memdir`** (Plan 13): `load_memories`, `walk_up`,
  `MemoryEntry`, `MemoryScope`. Walks up from cwd collecting `AGENTS.md`,
  `CLAUDE.md`, and nested `.claude/memories/*.md`; appends user-scoped
  entries from `extra_roots`; dedupes by `(scope, name)`. Concrete
  `pathlib.Path` per STATE.md decision. Ports CCB `src/memdir/**`. 9-test
  suite.
- **`claude_code_sdk.skills`** (Plan 11): `Skill`, `SkillParseError`,
  `parse_skill`, `parse_skill_text`, `discover_skills`. YAML frontmatter
  parser for `SKILL.md` files plus multi-root discovery with last-writer-
  wins dedupe by skill name; malformed files and missing roots are
  silently skipped. Adds `pyyaml>=6` runtime dependency. Ports CCB
  `src/skills/**`. 12-test suite.
- **`claude_code_sdk.plugins`** (Plan 10): `PluginLoader`, `LoadedPlugin`,
  `PluginLoadError`, `PluginManifest`, `PluginHookSpec`,
  `PluginCommandSpec`, `load_manifest`. Pydantic v2 schema for
  `plugin.json`, multi-plugin discovery via `*/plugin.json` glob, dotted
  `"pkg.module:object"` handler resolution via `importlib`, and
  `HookRegistry` integration (round-trip dispatch verified). Ports CCB
  `src/plugins/**` + plugin side of `src/utils/hooks/registerHook.ts`.
  9-test suite.
- **`claude_code_sdk.commands`** (Plan 12): `CommandRegistry`,
  `CommandNotFoundError`, `parse_invocation`, `Command`,
  `CommandContext`, `CommandResult`, `CommandHandler`. Case-insensitive
  registry with hidden-command filtering; `/name args` parser strips
  the leading slash; dispatch wraps plain-string handler returns into
  `CommandResult`. Built-in commands (`/init`, `/commit`, `/review`, ...)
  deferred to a follow-up phase. Ports CCB `src/commands/**`. 13-test
  suite.
- **`claude_code_sdk.permissions`** (Plan 15): `ToolPermissionContext`,
  `PermissionRule`, `parse_rule`, `match_rule`, plus re-export of
  `PermissionResult` from `claude_code_sdk.tools` (single source of
  truth). Rule syntax is `Tool` or `Tool(glob-pattern)` with primary
  field auto-selected by tool (e.g. `Bash`→`command`, `Read`→`path`).
  Precedence: deny > allow > ask; unmatched input yields ask with reason
  `"no matching rule"`. Ports CCB `src/permissions/**` +
  `src/ToolPermissionContext.ts`. 13-test suite.
- **`claude_code_sdk.providers`** (Plan 08): `AnthropicProvider`,
  `BedrockProvider`, `VertexProvider`, `OpenAICompatProvider`,
  `GlmProvider`, plus the `Provider` Protocol + `CompletionRequest` /
  `Message` / `StreamEvent` / `ProviderError` primitives. All HTTP
  providers use `httpx.AsyncClient` with SSE decoding; `boto3` /
  `google-auth` are lazy-imported via new optional extras
  `claude-code-sdk[bedrock]` and `claude-code-sdk[vertex]`.
  `AnthropicProvider` rejects `base_url` ending in `/v1` to prevent the
  `/v1/v1/messages` 404 regression (cf. repo memory
  *Claude Code Anthropic runtime URL normalization*). Ports CCB
  `src/services/api/**` per CONTEXT D-18. 18-test suite.

### Known gaps

- Four of twelve barrels are placeholder-only (mcp, hooks, memdir,
  skills, plugins, commands, permissions, providers populated in Plans
  07+09+13+11+10+12+15+08); remaining four drain over milestones
  0.2.x -- 0.5.x.
- Pyright runs with `continue-on-error: true` during alpha carve-in; will be
  hard-failed once all barrels are populated.

[Unreleased]: https://github.com/redpanda321/claude-code-sdk-python/compare/HEAD...HEAD
