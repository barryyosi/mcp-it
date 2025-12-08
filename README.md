# mcp-it

![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Status](https://img.shields.io/badge/status-active-success)

> **Inject your CLI tools directly into your Agentic pair-programmer's instructions file.**

**mcp-it** Automatically harvests commands, options, and descriptions from any CLI and injects them as structured tools into your `AGENTS.md`, `CLAUDE.md`, or any other instruction file.

---

## Quick Start

Clone, install, and run globally.

```bash
git clone https://github.com/barryyosi/mcp-it.git
cd mcp-it
uv sync
uv tool install .
```

## 📖 Usage Guide

Inject tools into `AGENTS.md` anywhere:
```bash
mcp-it <cli_executable> <target_file> --create-if-missing
```

Preview without writing:
```bash
mcp-it <cli_executable> <target_file> --dry-run
```

### Example

Inject the GitHub CLI tools into `AGENTS.md` (creating the file if it does not exist):
```bash
mcp-it gh AGENTS.md --create-if-missing
```


## Contributions are welcome! 🤝

---
