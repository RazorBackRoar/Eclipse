# Eclipse

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-arm64-brightgreen.svg)](https://support.apple.com/en-us/HT211814)
[![PySide6](https://img.shields.io/badge/PySide6-Qt6-orange.svg)](https://doc.qt.io/qtforpython/)

```text
███████╗ ██████╗██╗     ██╗██████╗ ███████╗███████╗
██╔════╝██╔════╝██║     ██║██╔══██╗██╔════╝██╔════╝
█████╗  ██║     ██║     ██║██████╔╝███████╗█████╗
██╔══╝  ██║     ██║     ██║██╔═══╝ ╚════██║██╔══╝
███████╗╚██████╗███████╗██║██║     ███████║███████╗
╚══════╝ ╚═════╝╚══════╝╚═╝╚═╝     ╚══════╝╚══════╝
```

> **AI workspace configuration manager for macOS.**
> Centralize, version, and export AI agent configs across Claude Code, Codex, Cursor, Windsurf, and OpenCode — from a single local library.

---

## Features

- **Library-First** — tool-agnostic, folder-based store of agents, skills, and rules
- **Jinja2 Rendering** — converts library objects into tool-specific file formats on export
- **Multi-IDE Export** — adapters for Claude Code, Codex, Cursor, Windsurf, and OpenCode
- **Import Pipeline** — scan local directories, drop files, or pull from GitHub URLs
- **Native macOS UI** — dark-themed PySide6 interface
- **Apple Silicon Native** — arm64 build optimized for M1/M2/M3/M4 chips

---

## Installation

1. Download the latest `Eclipse.dmg` from [Releases](https://github.com/RazorBackRoar/Eclipse/releases)
2. Open the DMG and drag `Eclipse.app` to `/Applications`
3. First launch — right-click the app → **Open** to bypass Gatekeeper on the ad-hoc signed build

---

## Usage

1. **Import** — scan a local directory, drop files into the panel, or paste a GitHub URL
2. **Browse** — view your agent library organized by type and tag
3. **Export** — select a target IDE and Eclipse writes the correct config format to the right location

---

## Development

### Requirements

- Python 3.14
- macOS 12.0+
- [uv](https://github.com/astral-sh/uv)

### Setup

```bash
git clone https://github.com/RazorBackRoar/Eclipse.git
cd Eclipse
uv sync
uv run python -m agentbox.main
```

### Build

```bash
razorbuild Eclipse
# Output: dist/Eclipse.dmg
```

### Lint & Test

```bash
uv run ruff check .
uv run ty check src --python-version 3.14
uv run pytest tests/ -q
```

---

## Project Structure

```text
Eclipse/
├── src/agentbox/
│   ├── main.py           # Entry point
│   ├── models.py         # LibraryItem dataclass
│   ├── storage.py        # Atomic library read/write
│   ├── render.py         # Jinja2 rendering engine
│   ├── paths.py          # Path resolution
│   ├── exporters/        # IDE-specific adapters
│   │   ├── claude_code.py
│   │   ├── codex.py
│   │   ├── cursor.py
│   │   ├── windsurf.py
│   │   └── opencode.py
│   ├── importers/        # Import pipeline
│   │   ├── scanner.py
│   │   ├── local_drop.py
│   │   ├── github_url.py
│   │   └── save_to_library.py
│   ├── templates/        # Jinja2 templates
│   └── ui/               # PySide6 GUI
├── assets/
├── tests/
└── Eclipse.spec
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.
Copyright © 2026 RazorBackRoar
