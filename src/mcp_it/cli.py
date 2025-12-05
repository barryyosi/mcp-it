import shutil
from pathlib import Path

import typer

from .agents import inject_tools_section, load_agents_md, render_tools_section, write_agents
from .command_discovery import collect_help_text, discover_commands, discover_options

app = typer.Typer(
    add_completion=False,
    help="Expose a CLI application's commands inside an AGENTS.md-style file for agentic pair programmers.",
)


def resolve_cli_path(cli_path: str, workdir: Path) -> Path:
    candidate = Path(cli_path)
    if not candidate.is_absolute():
        relative = (workdir / cli_path).resolve()
        if relative.exists():
            candidate = relative
        else:
            resolved = shutil.which(cli_path)
            if resolved:
                candidate = Path(resolved)

    if not candidate.exists():
        raise FileNotFoundError(f"CLI executable not found: {cli_path}")
    return candidate


def resolve_agents_path(agents_arg: str, workdir: Path) -> Path:
    path = Path(agents_arg)
    if not path.is_absolute():
        path = (workdir / agents_arg).resolve()
    return path


@app.command()
def expose(
    cli_path: str = typer.Argument(..., help="Path or name of the CLI executable (e.g., gh)."),
    agents_file: str = typer.Argument(
        "AGENTS.md",
        help="AGENTS.md-like file to update. (CLUADE.md, GEMINI.md, etc. are also supported.)",
        show_default=True,
    ),
    workdir: Path | None = typer.Option(
        None,
        "--workdir",
        help="Working directory for resolving paths and running CLI help commands.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Optional path to write the updated AGENTS file to instead of overwriting the input.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Print the updated AGENTS content to stdout without writing to disk.",
    ),
    exhaustive_help: bool = typer.Option(
        False,
        "--all",
        help="Try an exhaustive help call (help --all) before standard help discovery.",
    ),
    create_if_missing: bool = typer.Option(
        False,
        "--create-if-missing",
        help="Create the AGENTS file if it does not exist yet.",
    ),
    max_help_chars: int = typer.Option(
        1500,
        "--max-help-chars",
        help="Max characters of help text to embed; larger help is truncated and written to a sidecar file.",
    ),
    help_output: Path | None = typer.Option(
        None,
        "--help-output",
        help="Path to write full help text when it exceeds the max embedded length (defaults next to AGENTS file).",
    ),
) -> None:
    resolved_workdir = (workdir or Path.cwd()).resolve()

    try:
        cli_executable = resolve_cli_path(cli_path, resolved_workdir)
    except FileNotFoundError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    agents_instructions_path = resolve_agents_path(agents_file, resolved_workdir)
    target_path = output.resolve() if output else agents_instructions_path

    try:
        base_content = load_agents_md(agents_instructions_path)
    except FileNotFoundError as exc:
        if create_if_missing:
            base_content = ""
        else:
            typer.echo(f"Agent instructions file not found: {agents_instructions_path}", err=True)
            raise typer.Exit(code=1) from exc

    help_text = collect_help_text(cli_executable, exhaustive=exhaustive_help, workdir=resolved_workdir)
    commands = discover_commands(help_text)
    options = discover_options(help_text)
    if not commands and not options:
        typer.echo(
            f"No commands or options discovered from `{cli_executable}`. "
            "Try running with --all or verify the CLI supports help output.",
            err=True,
        )
        raise typer.Exit(code=1)

    truncated = False
    help_excerpt = help_text
    help_file_path: Path | None = None
    help_path_display: str | None = None
    if help_text and max_help_chars > 0 and len(help_text) > max_help_chars:
        truncated = True
        help_excerpt = help_text[:max_help_chars].rstrip() + "\n...\n(truncated)"
        default_help_path = (
            agents_instructions_path.parent / "AGENTS" / "tools" / f"{cli_executable.name}-help.txt"
        )
        candidate_path = help_output or default_help_path
        help_file_path = (
            candidate_path
            if candidate_path.is_absolute()
            else (resolved_workdir / candidate_path).resolve()
        )
        if dry_run:
            typer.echo(f"[dry-run] Would write full help to {help_file_path}")
            help_file_path = None
        else:
            help_file_path.parent.mkdir(parents=True, exist_ok=True)
            help_file_path.write_text(help_text)
        if help_file_path:
            try:
                help_path_display = str(help_file_path.relative_to(agents_instructions_path.parent))
            except ValueError:
                help_path_display = str(help_file_path)

    cli_label = cli_executable.name
    tools_block = render_tools_section(
        cli_label,
        commands,
        options=options,
        help_excerpt=help_excerpt,
        full_help_path=help_file_path,
        help_path_display=help_path_display,
        truncated=truncated,
    )
    updated_content = inject_tools_section(base_content, tools_block)

    if dry_run:
        typer.echo(updated_content)
        return

    write_agents(target_path, updated_content)
    typer.echo(f"Updated {target_path} with {len(commands)} commands from `{cli_label}`.")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
