# Eclipse

> Workspace context source: `/Users/home/Workspace/Apps/.code-analysis/` (`AGENTS.md`, `monorepo-analysis.md`, `essential-queries.md`).

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-Native-brightgreen.svg)](https://support.apple.com/en-us/HT211814)
[![PySide6](https://img.shields.io/badge/PySide6-Qt6-orange.svg)](https://doc.qt.io/qtforpython/)

```text
███████╗ ██████╗██╗     ██╗██████╗ ███████╗███████╗
██╔════╝██╔════╝██║     ██║██╔══██╗██╔════╝██╔════╝
█████╗  ██║     ██║     ██║██████╔╝███████╗█████╗
██╔══╝  ██║     ██║     ██║██╔═══╝ ╚════██║██╔══╝
███████╗╚██████╗███████╗██║██║     ███████║███████╗
╚══════╝ ╚═════╝╚══════╝╚═╝╚═╝     ╚══════╝╚══════╝
```

> **Canonical AI Workspace Configuration Manager**
> Centralize, version, and export AI agent configs across Claude Code, Codex, Cursor, Windsurf, and OpenCode — from a single local library.

---

## Features

- **Library-First** — tool-agnostic folder-based store of agents, skills, and rules
- **Jinja2 Rendering** — converts library objects into tool-specific file formats
- **Multi-IDE Export** — adapters for Claude Code, Codex, Cursor, Windsurf, OpenCode
- **Import Pipeline** — scan local directories, drop files, or pull from GitHub URLs
- **PySide6 GUI** — native macOS dark-themed interface
- **Apple Silicon Native** — optimized for M1/M2/M3 chips

---

## Installation

1. Download the latest `Eclipse.dmg` from [Releases](https://github.com/RazorBackRoar/Eclipse/releases)
2. Drag `Eclipse.app` to `/Applications`
3. **First Launch** — ad-hoc signed build, so Gatekeeper will prompt once:
   - Right-click `Eclipse.app` in Applications → **Open**
   - Click **Open** in the confirmation dialog — this only needs to be done once

---

## Development

This project uses `.razorcore` for build tooling.

### Prerequisites

- Python 3.14
- macOS 11.0+

### Setup

```bash
cd Apps/Eclipse
uv sync
uv run python -m agentbox.main
```

### Common Commands

| Command | Purpose |
|---------|---------|
| `eclipsepush` | Bump version, lint, commit, push |
| `eclipsebuild` | Full build → PyInstaller → DMG |
| `razorbuild Eclipse` | Same as eclipsebuild |
| `uv run ruff check .` | Lint |
| `uv run ty check src --python-version 3.14` | Type check |
| `uv run pytest tests/ -q` | Tests |

### Architecture

```
src/agentbox/
├── main.py           ← Entry point
├── models.py         ← LibraryItem dataclass (source of truth)
├── storage.py        ← Atomic library read/write
├── render.py         ← Jinja2 rendering engine
├── paths.py          ← All path resolution (use this, never ~)
├── exporters/        ← One adapter per IDE target
│   ├── claude_code.py
│   ├── codex.py
│   ├── cursor.py
│   ├── windsurf.py
│   └── opencode.py
├── importers/        ← Import pipeline
│   ├── scanner.py
│   ├── local_drop.py
│   ├── github_url.py
│   └── save_to_library.py
├── templates/        ← Jinja2 templates (bundled in Eclipse.spec)
└── ui/               ← PySide6 GUI
```

### Build

```bash
eclipsebuild
# or
razorbuild Eclipse
```

DMG layout (locked across all RazorBackRoar apps):
- Window: 600×350 · Icon size: 100
- App icon: (175, 150) · Applications link: (425, 150)
- Ad-hoc signed (`Signing identity: -`, RazorBackRoar)

---

## Known Issues (pending follow-up pass)

- `src/agentbox/ui/main_window.py` — `QSize` used without import
- `LibraryListPanel` — `self.app` and `self.items` referenced but not initialized in class
- `src/agentbox/importers/scanner.py` — `_is_under_named_dir()` defined but unused
- `save_detected_to_library()` — typed for `tuple[str, str, Path]` but scanner yields `DetectedItem`; caller/callee contract needs alignment

---

## License

MIT © 2026 RazorBackRoar
