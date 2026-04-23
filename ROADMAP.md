# Roadmap

`claude-code-sdk` is a library-first Python port of the Claude Code Builder
(CCB) TypeScript package. Milestones are ordered by **downstream consumer
demand**, not alphabetically.

## 0.1.x -- Foundations (this phase, Phase 999.2)

- [x] PEP 621 scaffold: `src/`-layout, hatchling + hatch-vcs, `py.typed`, MIT license.
- [x] 12 public barrels declared: `tools`, `adapters`, `mcp`, `providers`,
      `hooks`, `plugins`, `skills`, `commands`, `memdir`, `subagents`,
      `permissions`, `compaction`. All ship with CCB-drain-source docstrings.
- [x] `tools.Tool` Protocol (runtime-checkable) + supporting dataclasses
      (`ToolContext`, `ToolResult`, `PermissionResult`, `ToolCallProgress`).
- [x] `adapters.claude_agent_sdk`: bidirectional bridge to Anthropic's
      `SdkMcpTool` (lazy-imported optional extra).
- [x] CI matrix on 3.11 / 3.12 / 3.13: ruff + pytest + pyright (soft-fail).
- [x] Docs: README, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, this ROADMAP,
      CHANGELOG.
- [x] Release workflow wired (OIDC trusted publishing) but **dormant** -- no
      tag pushed yet.
- [ ] First PyPI publish (`0.1.0a1`) -- follow-up phase.

## 0.2.x -- `tools` tier 1

Drain the most-used CCB built-in tools from
[`claude-code-sdk-ts/src/tools`](https://github.com/redpanda321/claude-code-sdk-ts/tree/main/src/tools):

- [ ] `Bash`, `BashOutput`, `KillShell`
- [ ] `FileRead`, `FileEdit`, `FileWrite`
- [ ] `Glob`, `Grep`
- [ ] `TodoWrite`

All ported tools implement the `tools.Tool` Protocol and ship with parity
tests against the TypeScript sibling's fixtures.

## 0.3.x -- `providers`

Multi-provider LLM layer. Drain order reflects current traffic share:

- [ ] Anthropic (native)
- [ ] AWS Bedrock
- [ ] Google Vertex
- [ ] OpenAI-compatible (LiteLLM, OpenRouter, groq, ...)
- [ ] Z.ai GLM

Each provider conforms to a shared `Provider` Protocol (to be carved out in
this milestone).

## 0.4.x -- `mcp` + `hooks` + `plugins`

- [ ] `mcp`: MCP server registry + transport helpers, ported from
      `claude-code-sdk-ts/src/mcp`.
- [ ] `hooks`: pre/post-tool + pre/post-agent lifecycle hooks, ported from
      `claude-code-sdk-ts/src/hooks`.
- [ ] `plugins`: first-party plugin ecosystem + loader, ported from
      `claude-code-sdk-ts/src/plugins`.

## 0.5.x -- `skills` + `commands` + `memdir` + `subagents` + `permissions` + `compaction`

Remaining six barrels. Each ports directly from its TypeScript sibling:

- [ ] `skills` -- reusable prompt + tool bundles (`.claude/skills/` format).
- [ ] `commands` -- slash-command registry.
- [ ] `memdir` -- persistent memory scopes.
- [ ] `subagents` -- delegated-task runner.
- [ ] `permissions` -- allow/deny rule engine.
- [ ] `compaction` -- context-window compaction strategies.

## 1.0.0 -- Parity + API freeze

All 12 barrels populated, parity with CCB TypeScript `v1.x`, API stabilised,
full documentation, coverage reporting, pyright hard-fail in CI.

## Non-goals

- **CLI/TUI**: lives in a separate repo; `claude-code-sdk` never adds
  `[project.scripts]`.
- **GUI**: out of scope.
- **Cross-process agent orchestration**: use a separate coordinator; this
  package provides the in-process building blocks only.
