import re
import subprocess
from pathlib import Path
from typing import Iterable, Sequence

from .types import CommandInfo, OptionInfo

COMMAND_SECTION_HEADERS = (
    "available commands",
    "commands",
    "command groups",
    "management commands",
    "subcommands",
)
OPTION_SECTION_HEADERS = (
    "options",
    "flags",
)

# Matches lines like "  clone          Clone a repository"
_COMMAND_PATTERN = re.compile(r"^\s{0,6}([A-Za-z0-9][\w:.\-/]*)\s{2,}(.+?)\s*$")
_OPTION_PATTERN = re.compile(
    r"^\s{0,6}"
    r"(-{1,2}[^\s,]+(?:\s*,\s*-{1,2}[^\s,]+)*)"
    r"(?:\s{2,}(.+?))?"
    r"\s*$"
)


def collect_help_text(cli_path: Path, exhaustive: bool = False, workdir: Path | None = None) -> str:
    """Run a CLI's help commands and return combined output."""
    attempts: list[Sequence[str]] = []
    exe = str(cli_path)
    if exhaustive:
        attempts.append([exe, "help", "--all"])
    attempts.extend([[exe, "--help"], [exe, "help"], [exe, "-h"]])

    outputs: list[str] = []
    for argv in attempts:
        try:
            result = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                cwd=workdir,
            )
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"CLI executable not found: {cli_path}") from exc

        stream = result.stdout or result.stderr
        if stream:
            outputs.append(stream.strip())
        if result.returncode == 0 and stream:
            break

    return "\n\n".join(outputs).strip()


def discover_commands(help_text: str) -> list[CommandInfo]:
    """Extract commands and descriptions from CLI help text."""
    if not help_text:
        return []

    lines = help_text.splitlines()
    commands = list(_extract_command_sections(lines))

    if not commands:
        commands = list(_extract_loose_commands(lines))

    return _dedupe_commands(commands)


def discover_options(help_text: str) -> list[OptionInfo]:
    """Extract option/flag descriptions from CLI help text."""
    if not help_text:
        return []

    lines = help_text.splitlines()
    options = list(_extract_option_sections(lines))
    if not options:
        options = list(_extract_loose_options(lines))
    return _dedupe_options(options)


def _extract_command_sections(lines: Sequence[str]) -> Iterable[CommandInfo]:
    collecting = False
    for line in lines:
        lowered = line.strip().lower()
        if any(lowered.startswith(header) for header in COMMAND_SECTION_HEADERS):
            collecting = True
            continue

        if collecting and not line.strip():
            collecting = False
            continue

        if collecting:
            command = _match_command_line(line)
            if command:
                yield command


def _extract_option_sections(lines: Sequence[str]) -> Iterable[OptionInfo]:
    collecting = False
    for line in lines:
        lowered = line.strip().lower()
        if any(lowered.startswith(header) for header in OPTION_SECTION_HEADERS):
            collecting = True
            continue

        if collecting and not line.strip():
            collecting = False
            continue

        if collecting:
            option = _match_option_line(line)
            if option:
                yield option


def _extract_loose_commands(lines: Sequence[str]) -> Iterable[CommandInfo]:
    for line in lines:
        if "usage" in line.lower():
            continue

        command = _match_command_line(line)
        if command:
            yield command


def _extract_loose_options(lines: Sequence[str]) -> Iterable[OptionInfo]:
    for line in lines:
        if "usage" in line.lower():
            continue

        option = _match_option_line(line)
        if option:
            yield option


def _match_command_line(line: str) -> CommandInfo | None:
    match = _COMMAND_PATTERN.match(line)
    if not match:
        return None

    name, description = match.groups()
    return CommandInfo(name=name.strip(), description=description.strip())


def _match_option_line(line: str) -> OptionInfo | None:
    match = _OPTION_PATTERN.match(line)
    if not match:
        return None

    flags, description = match.groups()
    return OptionInfo(flags=flags.strip(), description=(description or "").strip())


def _dedupe_commands(commands: Sequence[CommandInfo]) -> list[CommandInfo]:
    seen = {}
    ordered: list[CommandInfo] = []
    for command in commands:
        if command.name in seen:
            continue
        seen[command.name] = True
        ordered.append(command)
    return ordered


def _dedupe_options(options: Sequence[OptionInfo]) -> list[OptionInfo]:
    seen = {}
    ordered: list[OptionInfo] = []
    for opt in options:
        if opt.flags in seen:
            continue
        seen[opt.flags] = True
        ordered.append(opt)
    return ordered
