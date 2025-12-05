from dataclasses import dataclass


@dataclass
class CommandInfo:
    """Represents a CLI command surfaced to agents."""

    name: str
    description: str = ""


@dataclass
class OptionInfo:
    """Represents an option/flag exposed by the CLI."""

    flags: str
    description: str = ""
