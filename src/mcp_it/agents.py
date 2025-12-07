import re
from pathlib import Path
from typing import Iterable, Tuple

from .types import CommandInfo, OptionInfo

TOOLS_START = "<!-- tools start -->"
TOOLS_END = "<!-- tools end -->"
CLI_HEADING_PATTERN = re.compile(r"^## External CLI tools for `([^`]+)`\s*$")


def render_tools_section(
    cli_label: str,
    commands: Iterable[CommandInfo],
    options: Iterable[OptionInfo] | None = None,
    help_excerpt: str | None = None,
    full_help_path: Path | None = None,
    help_path_display: str | None = None,
    truncated: bool = False,
) -> str:
    """Build the Markdown block describing discovered CLI commands and options."""
    commands_list = list(commands)
    options_list = list(options or [])
    lines = [
        TOOLS_START,
        f"## External CLI tools for `{cli_label}`",
        f"When interaction with `{cli_label}` is required, you can utilize the following tools:",
        "",
    ]

    for command in commands_list:
        lines.append(f"### {command.name}")
        if command.description:
            lines.append(f"Description: {command.description}")
        lines.append(f"Invocation: `{cli_label} {command.name} ...`")
        if options_list:
            lines.append("Common options:")
            for option in options_list:
                if option.description:
                    lines.append(f"- `{option.flags}` — {option.description}")
                else:
                    lines.append(f"- `{option.flags}`")
        lines.append("")

    if help_excerpt:
        lines.append("Help excerpt:")
        lines.append("```")
        lines.append(help_excerpt.strip())
        lines.append("```")
        path_label = help_path_display or (str(full_help_path) if full_help_path else None)
        if truncated:
            if path_label:
                lines.append(f"Full help is available at `{path_label}`.")
            else:
                lines.append("Full help was truncated; re-run with a higher limit or provide --help-output.")
        elif path_label:
            lines.append(f"Full help saved at `{path_label}`.")

    lines.append(
        f"Notes: Arguments and flags vary by command; run `{cli_label} <command> --help` for details."
    )
    lines.append(TOOLS_END)

    return "\n".join(lines) + "\n"


def inject_tools_section(content: str, tools_block: str) -> str:
    """Insert or replace the tools section within AGENTS.md content."""
    tools_inner = _strip_outer_tools_markers(tools_block, fallback=content.strip())

    block_pattern = re.compile(
        rf"{re.escape(TOOLS_START)}.*?{re.escape(TOOLS_END)}",
        flags=re.DOTALL,
    )

    if TOOLS_START in normalized_content and TOOLS_END in normalized_content:
        existing_inner = _extract_tools_block(normalized_content)
        merged_inner = _merge_tools_blocks(existing_inner, tools_inner)
        content_without_blocks = block_pattern.sub("", normalized_content).rstrip()
        separator = "\n\n" if content_without_blocks else ""
        return f"{content_without_blocks}{separator}{TOOLS_START}\n{merged_inner.strip()}\n{TOOLS_END}\n"

    if TOOLS_START in normalized_content or TOOLS_END in normalized_content:
        sanitized = normalized_content.replace(TOOLS_START, "").replace(TOOLS_END, "").strip()
        normalized_content = sanitized

    separator = "\n\n" if normalized_content.strip() else ""
    return f"{normalized_content}{separator}{TOOLS_START}\n{tools_inner.strip()}\n{TOOLS_END}\n".lstrip("\n")


def load_agents_md(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"AGENTS file not found: {path}")
    return path.read_text()


def write_agents(path: Path, content: str) -> None:
    path.write_text(content)


def _extract_tools_block(content: str) -> str:
    pattern = re.compile(
        rf"{re.escape(TOOLS_START)}(.*?){re.escape(TOOLS_END)}",
        flags=re.DOTALL,
    )
    match = pattern.search(content)
    if match:
        return match.group(1).strip()
    return ""


def _strip_outer_tools_markers(text: str, fallback: str = "") -> str:
    inner = _extract_tools_block(text)
    return inner if inner else fallback


def _split_cli_sections(block: str) -> Tuple[list[str], dict[str, str]]:
    lines = block.strip().splitlines() if block.strip() else []
    order: list[str] = []
    sections: dict[str, list[str]] = {}
    current_label: str | None = None

    for line in lines:
        heading = CLI_HEADING_PATTERN.match(line.strip())
        if heading:
            label = heading.group(1)
            if current_label and current_label in sections:
                sections[current_label].append("")  # preserve spacing
            current_label = label
            if label not in order:
                order.append(label)
            sections.setdefault(label, []).append(line)
            continue

        if current_label:
            sections[current_label].append(line)

    flattened = {k: "\n".join(v).strip() for k, v in sections.items()}
    return order, flattened


def _merge_tools_blocks(existing_block: str, new_block: str) -> str:
    order, sections = _split_cli_sections(existing_block)
    new_order, new_sections = _split_cli_sections(new_block)

    for label in new_order:
        if label not in order:
            order.append(label)
        sections[label] = new_sections[label]

    merged_sections = [sections[label].strip() for label in order if label in sections]
    return "\n\n".join(merged_sections).strip() + "\n"

