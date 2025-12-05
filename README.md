# mcp-it

MCP-aware tooling injector for agentic pair programmers. Point it at any CLI, and it will harvest commands + options, render a Markdown tools section, and inject/merge it into your `AGENTS.md` so agents know what they can call.

## Why
- Keep agent instructions in sync with the real CLI surface area.
- Support multiple CLIs in one `AGENTS.md` without clobbering existing sections.
- Avoid giant inline help by auto-truncating and offloading full docs to sidecar files.

## Quick start
```bash
uv sync
uv run mcp-it gh AGENTS.md --create-if-missing
```
Preview only:
```bash
uv run mcp-it gh AGENTS.md --dry-run
```
Force truncation and sidecar help:
```bash
uv run mcp-it gh AGENTS.md --max-help-chars 1200
# full help saved to AGENTS/tools/gh-help.txt (or a custom path via --help-output)
```

## What it does
- Runs `<cli> --help` (and variants) to harvest commands, descriptions, and common options.
- Injects or merges a block delimited by:
  - `<!-- mcp-it tools start -->`
  - `<!-- mcp-it tools end -->`
- Keeps multiple CLI sections; re-runs update the matching CLI while preserving others.
- Truncates embedded help (default 1500 chars) and writes the full text to `AGENTS/tools/<cli>-help.txt` unless you override with `--help-output`.

Example snippet (truncated for brevity):
```
<!-- mcp-it tools start -->
## External CLI tools for `gh`
When interaction with `gh` is required, you can utilize the following tools:

### repo
Description: Manage repositories
Invocation: `gh repo ...`
Common options:
- `--help` — Show help for command

Help excerpt:
```
gh <command> <subcommand> [flags]
...
(truncated)
```
Full help is available at `AGENTS/tools/gh-help.txt`.
<!-- mcp-it tools end -->
```

## CLI options
- `--workdir`: Resolve paths and run help from a specific directory.
- `--output/-o`: Write the updated content to another path.
- `--create-if-missing`: Create `AGENTS.md` if it does not exist.
- `--all`: Try `help --all` before standard help discovery.
- `--dry-run`: Print the updated content without writing.
- `--max-help-chars`: Characters of help to embed before truncation (default 1500).
- `--help-output`: Where to write the full help when truncated (default `AGENTS/tools/<cli>-help.txt`).

## Notes and limitations
- Parsing is heuristic; some CLIs format help idiosyncratically. If discovery fails, try `--all` or point to a CLI that emits standard help.
- Option lists are shallow; for complex CLIs you may want per-command parsing in the future.
- Re-running is idempotent for each CLI block; we merge by CLI heading.

## Development
- Requires Python 3.13+.
- Install deps: `uv sync`
- Run CLI locally: `uv run mcp-it --help`

Contributions welcome: tidy up parsers per CLI family, add tests, or extend help introspection. Submit issues/PRs with repro steps or sample help outputs.***
