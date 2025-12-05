# mcp-it

Expose an external CLI's commands into an AGENTS.md-style file so an agentic pair programmer knows which tools are available.

## Quick start

```bash
uv sync
uv run mcp-it <CLI_EXECUTABLE> AGENTS.md --create-if-missing
```

- `AGENTS.md` defaults to `./AGENTS.md` if omitted.
- Add `--all` to try `help --all` before standard help discovery.
- Use `--dry-run` to preview the rewritten file without saving.

## What it does

- Runs the target CLI's help command to harvest commands + descriptions (heuristic parser).
- Renders a Markdown block describing each command as a "tool" for the agent.
- Injects or replaces that block between markers:
  - `<!-- tools start -->`
  - `<!-- tools end -->`

Example snippet inserted:

```
## External CLI tools for `gh`
When interaction with `gh` is required, you can utilize the following tools:

### repo
Description: Manage GitHub repositories
Invocation: `gh repo ...`
```

## CLI options

- `--workdir`: Run discovery and resolve paths relative to a directory (useful when invoked from elsewhere).
- `--output/-o`: Write the updated content to another path.
- `--create-if-missing`: Generate AGENTS.md if it is not present.
- `--all`: Attempt exhaustive help discovery via `help --all` before falling back to standard help.
- `--dry-run`: Print updated content to stdout without writing.
- `--max-help-chars`: Truncate embedded help to this length (defaults to 1500 chars).
- `--help-output`: Path to write the full help text if it exceeds the embed limit (defaults to `AGENTS/tools/<cli>-help.txt` alongside AGENTS.md).

## Notes and limitations

- Command discovery is heuristic; some CLIs format help differently. If no commands are found, rerun with `--all` or pass a CLI that supports standard help output.
- Arguments/flags are not parsed; the generated section points agents to run `<cli> <command> --help` for specifics.
