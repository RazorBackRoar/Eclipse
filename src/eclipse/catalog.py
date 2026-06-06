# src/agentbox/catalog.py
"""Template catalog for Eclipse workspace config generator.

Defines all categories and their starter templates with default content.
Templates can be edited in the UI and exported in normal or hidden form.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TemplateEntry:
    """A single exportable template file."""

    id: str
    category: str
    filename: str
    display_name: str
    default_content: str
    hidden_folder: str = ""
    normal_folder: str = ""


# ── Category definitions ─────────────────────────────────────────────────────────

CATEGORIES: list[dict[str, str]] = [
    {"id": "general", "label": "General", "group": "content"},
    {"id": "python", "label": "Python", "group": "content"},
    {"id": "codex", "label": "Codex", "group": "tools"},
    {"id": "cursor", "label": "Cursor", "group": "tools"},
    {"id": "windsurf", "label": "Windsurf", "group": "tools"},
    {"id": "opencode", "label": "OpenCode", "group": "tools"},
    {"id": "gemini", "label": "Gemini", "group": "tools"},
    {"id": "claude", "label": "Claude", "group": "tools"},
    {"id": "mlx_notes", "label": "MLX Notes", "group": "content"},
    {"id": "skills", "label": "Skills", "group": "content"},
    {"id": "plugins", "label": "Plugins", "group": "content"},
    {"id": "hooks", "label": "Hooks", "group": "content"},
    {"id": "agents", "label": "Agents", "group": "content"},
    {"id": "config", "label": "Config", "group": "content"},
    {"id": "schemas", "label": "Schemas", "group": "content"},
    {"id": "scripts", "label": "Scripts", "group": "content"},
    {"id": "src", "label": "Source", "group": "content"},
    {"id": "tests", "label": "Tests", "group": "content"},
    {"id": "mcp-configs", "label": "MCP Configs", "group": "tools"},
    {"id": "research", "label": "Research", "group": "content"},
    {"id": "rules", "label": "Rules", "group": "content"},
    {"id": "converter", "label": "Converter", "group": "utilities"},
    {"id": "export", "label": "Export", "group": "utilities"},
]

CATEGORY_IDS: list[str] = [c["id"] for c in CATEGORIES]


def category_label(category_id: str) -> str:
    for c in CATEGORIES:
        if c["id"] == category_id:
            return c["label"]
    return category_id


# ── Template registry ─────────────────────────────────────────────────────────────

def _build_catalog() -> list[TemplateEntry]:
    """Build the full template catalog with default content."""
    entries: list[TemplateEntry] = []

    # ── General ──────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="general-readme", category="general",
        filename="README.md", display_name="README.md",
        default_content=_GENERAL_README,
    ))
    entries.append(TemplateEntry(
        id="general-changelog", category="general",
        filename="CHANGELOG.md", display_name="CHANGELOG.md",
        default_content=_GENERAL_CHANGELOG,
    ))
    entries.append(TemplateEntry(
        id="general-howto", category="general",
        filename="HOWTO.md", display_name="HOWTO.md",
        default_content=_GENERAL_HOWTO,
    ))
    entries.append(TemplateEntry(
        id="general-notes", category="general",
        filename="NOTES.md", display_name="NOTES.md",
        default_content=_GENERAL_NOTES,
    ))
    entries.append(TemplateEntry(
        id="general-todo", category="general",
        filename="TODO.md", display_name="TODO.md",
        default_content=_GENERAL_TODO,
    ))

    # ── Python ───────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="python-pyproject", category="python",
        filename="pyproject.toml", display_name="pyproject.toml",
        default_content=_PYTHON_PYPROJECT,
    ))
    entries.append(TemplateEntry(
        id="python-ruff", category="python",
        filename="ruff.toml", display_name="ruff.toml",
        default_content=_PYTHON_RUFF,
    ))
    entries.append(TemplateEntry(
        id="python-ty", category="python",
        filename="ty.toml", display_name="ty.toml",
        default_content=_PYTHON_TY,
    ))
    entries.append(TemplateEntry(
        id="python-pytest", category="python",
        filename="pytest.ini", display_name="pytest.ini",
        default_content=_PYTHON_PYTEST,
    ))
    entries.append(TemplateEntry(
        id="python-requirements", category="python",
        filename="requirements.txt", display_name="requirements.txt",
        default_content=_PYTHON_REQUIREMENTS,
    ))
    entries.append(TemplateEntry(
        id="python-gitignore", category="python",
        filename=".gitignore", display_name=".gitignore",
        default_content=_PYTHON_GITIGNORE,
    ))

    # ── Codex ────────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="codex-agents", category="codex",
        filename="AGENTS.md", display_name="AGENTS.md",
        default_content=_CODEX_AGENTS,
        hidden_folder=".codex", normal_folder="codex",
    ))
    entries.append(TemplateEntry(
        id="codex-codex", category="codex",
        filename="codex.md", display_name="codex.md",
        default_content=_CODEX_CODEX,
        hidden_folder=".codex", normal_folder="codex",
    ))

    # ── Cursor ───────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="cursor-cursor", category="cursor",
        filename="CURSOR.md", display_name="CURSOR.md",
        default_content=_CURSOR_CURSOR,
        hidden_folder=".cursor", normal_folder="cursor",
    ))
    entries.append(TemplateEntry(
        id="cursor-rules", category="cursor",
        filename="rules.md", display_name="rules.md",
        default_content=_CURSOR_RULES,
        hidden_folder=".cursor/rules", normal_folder="cursor/rules",
    ))

    # ── Windsurf ─────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="windsurf-rules", category="windsurf",
        filename="rules.md", display_name="rules.md",
        default_content=_WINDSURF_RULES,
        hidden_folder=".windsurf", normal_folder="windsurf",
    ))
    entries.append(TemplateEntry(
        id="windsurf-workspace", category="windsurf",
        filename="workspace-notes.md", display_name="workspace-notes.md",
        default_content=_WINDSURF_WORKSPACE,
        hidden_folder=".windsurf", normal_folder="windsurf",
    ))

    # ── OpenCode ─────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="opencode-opencode", category="opencode",
        filename="OPENCODE.md", display_name="OPENCODE.md",
        default_content=_OPENCODE_MD,
        hidden_folder=".opencode", normal_folder="opencode",
    ))

    # ── Gemini ───────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="gemini-gemini", category="gemini",
        filename="GEMINI.md", display_name="GEMINI.md",
        default_content=_GEMINI_MD,
        hidden_folder=".gemini", normal_folder="gemini",
    ))

    # ── Claude ───────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="claude-claude", category="claude",
        filename="CLAUDE.md", display_name="CLAUDE.md",
        default_content=_CLAUDE_MD,
        hidden_folder=".claude", normal_folder="claude",
    ))

    # ── MLX Notes ────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="mlx-models", category="mlx_notes",
        filename="MODELS.md", display_name="MODELS.md",
        default_content=_MLX_MODELS,
    ))
    entries.append(TemplateEntry(
        id="mlx-ollama", category="mlx_notes",
        filename="OLLAMA.md", display_name="OLLAMA.md",
        default_content=_MLX_OLLAMA,
    ))
    entries.append(TemplateEntry(
        id="mlx-huggingface", category="mlx_notes",
        filename="HUGGINGFACE.md", display_name="HUGGINGFACE.md",
        default_content=_MLX_HUGGINGFACE,
    ))
    entries.append(TemplateEntry(
        id="mlx-lmstudio", category="mlx_notes",
        filename="LMSTUDIO.md", display_name="LMSTUDIO.md",
        default_content=_MLX_LMSTUDIO,
    ))
    entries.append(TemplateEntry(
        id="mlx-mlx", category="mlx_notes",
        filename="MLX.md", display_name="MLX.md",
        default_content=_MLX_MLX,
    ))

    # ── Skills ───────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="skills-skill", category="skills",
        filename="SKILL.md", display_name="SKILL.md",
        default_content=_SKILLS_SKILL,
        hidden_folder=".skills", normal_folder="skills",
    ))

    # ── Plugins ──────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="plugins-readme", category="plugins",
        filename="README.md", display_name="README.md",
        default_content=_PLUGINS_README,
        hidden_folder=".plugins", normal_folder="plugins",
    ))

    # ── Hooks ────────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="hooks-readme", category="hooks",
        filename="README.md", display_name="README.md",
        default_content=_HOOKS_README,
        hidden_folder=".hooks", normal_folder="hooks",
    ))

    # ── Config ───────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="config-readme", category="config",
        filename="README.md", display_name="README.md",
        default_content=_CONFIG_README,
        hidden_folder=".config", normal_folder="config",
    ))

    # ── Schemas ──────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="schemas-readme", category="schemas",
        filename="README.md", display_name="README.md",
        default_content=_SCHEMAS_README,
        hidden_folder=".schemas", normal_folder="schemas",
    ))

    # ── Scripts ──────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="scripts-readme", category="scripts",
        filename="README.md", display_name="README.md",
        default_content=_SCRIPTS_README,
        hidden_folder=".scripts", normal_folder="scripts",
    ))

    # ── Source ───────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="src-readme", category="src",
        filename="README.md", display_name="README.md",
        default_content=_SRC_README,
        hidden_folder=".src", normal_folder="src",
    ))

    # ── Tests ────────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="tests-readme", category="tests",
        filename="README.md", display_name="README.md",
        default_content=_TESTS_README,
        hidden_folder=".tests", normal_folder="tests",
    ))

    # ── MCP Configs ──────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="mcp-configs-readme", category="mcp-configs",
        filename="README.md", display_name="README.md",
        default_content=_MCP_CONFIGS_README,
        hidden_folder=".mcp-configs", normal_folder="mcp-configs",
    ))

    # ── Research ─────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="research-readme", category="research",
        filename="README.md", display_name="README.md",
        default_content=_RESEARCH_README,
        hidden_folder=".research", normal_folder="research",
    ))

    # ── Rules ────────────────────────────────────────────────────────────────
    entries.append(TemplateEntry(
        id="rules-rules", category="rules",
        filename="RULES.md", display_name="RULES.md",
        default_content=_RULES_RULES,
        hidden_folder=".rules", normal_folder="rules",
    ))

    return entries


_GENERAL_README = """\
# Project Name

> Brief description of this project.

## Overview

Describe the purpose, goals, and high-level architecture.

## Getting Started

```bash
uv sync
uv run python -m myproject
```

## Development

| Command | Purpose |
|---------|---------|
| `uv run ruff check .` | Lint |
| `uv run ty check src` | Type check |
| `uv run pytest tests/` | Tests |

## License

MIT
"""

_GENERAL_CHANGELOG = """\
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
-

### Changed
-

### Fixed
-
"""

_GENERAL_HOWTO = """\
# How-To Guide

## Setup

1. Install dependencies: `uv sync`
2. Run locally: `uv run python -m myproject`

## Common Tasks

### Adding a new feature
- Describe steps here.

### Running tests
```bash
uv run pytest tests/ -q
```
"""

_GENERAL_NOTES = """\
# Notes

## Architecture Decisions
-

## Open Questions
-

## References
-
"""

_GENERAL_TODO = """\
# TODO

## Priority
- [ ]

## Backlog
- [ ]

## Done
- [x]
"""

# ── Python templates ─────────────────────────────────────────────────────────────

_PYTHON_PYPROJECT = """\
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "myproject"
version = "0.1.0"
description = ""
authors = [{name = ""}]
requires-python = "==3.14.*"

dependencies = []

[project.scripts]
myproject = "myproject.main:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[dependency-groups]
dev = [
    "pytest>=9.0",
    "ruff>=0.15",
    "ty>=0.0.20",
]
"""

_PYTHON_RUFF = """\
# Ruff configuration
# https://docs.astral.sh/ruff/configuration/

target-version = "py314"
line-length = 100

[lint]
select = [
    "E", "W",    # pycodestyle
    "F",          # pyflakes
    "I",          # isort
    "UP",         # pyupgrade
    "B",          # bugbear
    "N",          # pep8-naming
    "D",          # pydocstyle
]

[lint.pydocstyle]
convention = "google"

[lint.isort]
known-first-party = ["myproject"]
lines-after-imports = 2

[lint.per-file-ignores]
"tests/**" = ["D"]
"""

_PYTHON_TY = """\
# Ty type checker configuration

[environment]
extra-paths = ["src"]

[src]
exclude = [
    "__pycache__",
    "*.egg-info",
    ".venv",
    "build",
    "dist",
]

[analysis]
respect-type-ignore-comments = true
"""

_PYTHON_PYTEST = """\
[pytest]
pythonpath = src
testpaths = tests
addopts = -q --tb=short
"""

_PYTHON_REQUIREMENTS = """\
# Core dependencies
# Prefer pyproject.toml [project.dependencies] over this file.
# Use this only for deployment environments that require requirements.txt.
"""

_PYTHON_GITIGNORE = """\
# Python
__pycache__/
*.py[cod]
*.egg-info/
*.egg
dist/
build/
.eggs/

# Virtual environments
.venv/
venv/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.pytest_cache/
htmlcov/
.coverage
.tox/
.nox/

# macOS
.DS_Store
Icon\\r

# Build artifacts
*.dmg
"""

# ── Codex templates ──────────────────────────────────────────────────────────────

_CODEX_AGENTS = """\
# AGENTS

## Purpose

Define agent behavior, constraints, and workspace rules for this project.

## Instructions

- Follow the coding style established in this repository.
- Run verification commands before considering work complete.
- Do not modify files outside the project scope.

## Verification

```bash
uv run ruff check .
uv run ty check src
uv run pytest tests/ -q
```

## Constraints

- Do not commit or push without explicit approval.
- Do not delete or overwrite existing files without confirmation.
- Preserve existing comments and docstrings.
"""

_CODEX_CODEX = """\
# Codex

Project-specific notes for Codex agent configuration.

## Workspace

- Project root: `.`
- Source: `src/`
- Tests: `tests/`

## Sandbox

Codex runs in a sandboxed environment. Ensure all dependencies
are declared in `pyproject.toml`.
"""

# ── Cursor templates ─────────────────────────────────────────────────────────────

_CURSOR_CURSOR = """\
# Cursor Rules

## Project Context

Describe the project purpose and key architecture decisions here.

## Coding Standards

- Follow existing code style and conventions.
- Use type hints for all function signatures.
- Write docstrings for public functions and classes.

## Verification

```bash
uv run ruff check .
uv run ty check src
uv run pytest tests/ -q
```

## Constraints

- Do not modify unrelated files.
- Do not introduce new dependencies without discussion.
- Preserve existing test coverage.
"""

_CURSOR_RULES = """\
---
description: Project rules
alwaysApply: false
---

Follow the project coding conventions and run verification
commands before finishing work.
"""

# ── Windsurf templates ───────────────────────────────────────────────────────────

_WINDSURF_RULES = """\
# Windsurf Rules

## Project Context

Describe the project and key constraints.

## Standards

- Follow the established code style.
- Run lint and type checks before finishing.
- Do not modify files outside project scope.

## Verification

```bash
uv run ruff check .
uv run ty check src
uv run pytest tests/ -q
```
"""

_WINDSURF_WORKSPACE = """\
# Workspace Notes

## Project Structure

- `src/` — Source code
- `tests/` — Test suite
- `docs/` — Documentation

## Key Files

- `pyproject.toml` — Project configuration
- `AGENTS.md` — Agent instructions
"""

# ── OpenCode templates ───────────────────────────────────────────────────────────

_OPENCODE_MD = """\
# OpenCode

## Project Context

Describe the project purpose and constraints.

## Instructions

- Follow existing code patterns.
- Run verification before completing tasks.
- Do not modify unrelated files.

## Verification

```bash
uv run ruff check .
uv run ty check src
uv run pytest tests/ -q
```
"""

# ── Gemini templates ─────────────────────────────────────────────────────────────

_GEMINI_MD = """\
# Gemini Instructions

## Project Context

Describe the project purpose, stack, and constraints.

## Coding Standards

- Follow the existing code style and conventions.
- Use type hints for all public interfaces.
- Write clear docstrings.

## Verification

```bash
uv run ruff check .
uv run ty check src
uv run pytest tests/ -q
```

## Constraints

- Do not commit or push without approval.
- Do not modify files outside the project scope.
- Preserve existing documentation.
"""

# ── Claude templates ─────────────────────────────────────────────────────────────

_CLAUDE_MD = """\
# Project Instructions

## Overview

Describe the project purpose and key context.

## Behavior

- Follow existing code patterns and conventions.
- Run verification commands before completing work.
- Do not modify files outside the project scope.

## Rules

- Do not commit or push without explicit approval.
- Do not delete or overwrite existing files.
- Preserve existing comments and documentation.

## Required Commands

```bash
uv run ruff check .
uv run ty check src
uv run pytest tests/ -q
```
"""

# ── MLX Notes templates ──────────────────────────────────────────────────────────

_MLX_MODELS = """\
# Local Models

## Model Inventory

| Model | Source | Quant | Context | RAM | Use Case |
|-------|--------|-------|---------|-----|----------|
|       |        |       |         |     |          |

## Notes

-
"""

_MLX_OLLAMA = """\
# Ollama Notes

## Installed Models

| Model | Size | Quant | Context | Performance |
|-------|------|-------|---------|-------------|
|       |      |       |         |             |

## Best Settings

-

## Known Issues

-
"""

_MLX_HUGGINGFACE = """\
# Hugging Face Notes

## Downloaded Models

| Model | Repo | Quant | Context | RAM Est. |
|-------|------|-------|---------|----------|
|       |      |       |         |          |

## Usage Notes

-
"""

_MLX_LMSTUDIO = """\
# LM Studio Notes

## Loaded Models

| Model | Format | Quant | Context | VRAM |
|-------|--------|-------|---------|------|
|       |        |       |         |      |

## Prompt Notes

-

## Performance Notes

-
"""

_MLX_MLX = """\
# MLX Notes

## Converted Models

| Model | Original | MLX Format | Performance |
|-------|----------|------------|-------------|
|       |          |            |             |

## Conversion Steps

1.

## Best Settings

-
"""

# ── Skills templates ─────────────────────────────────────────────────────────────

_SKILLS_SKILL = """\
# Skill Name

> Reusable workflow instructions for a specific task.

## Purpose

Describe what this skill does and when to use it.

## Steps

1.
2.
3.

## Inputs

- Describe required inputs.

## Outputs

- Describe expected outputs.

## Notes

- This is a reusable workflow instruction, not agent policy.
- AGENTS.md defines policy/rules/context for agents.
- SKILL.md defines reusable workflow instructions.
"""

# ── Plugins templates ────────────────────────────────────────────────────────────

_PLUGINS_README = """\
# Plugins

## Overview

This folder contains plugins for the project.

## Structure

```
plugins/
├── plugin-name/
│   ├── manifest.json
│   └── ...
```

## Adding a Plugin

1. Create a folder under `plugins/`.
2. Add a `manifest.json` describing the plugin.
3. Implement the plugin logic.
"""

# ── Hooks templates ──────────────────────────────────────────────────────────────

_HOOKS_README = """\
# Hooks

## Overview

This folder contains lifecycle hooks for the project.

## Structure

```
hooks/
├── pre-commit
├── post-build
└── ...
```

## Adding a Hook

1. Create a script under `hooks/`.
2. Make it executable: `chmod +x hooks/my-hook`.
3. Document its trigger condition.
"""

# ── Agents templates ─────────────────────────────────────────────────────────────

_AGENTS_AGENTS = """\
# AGENTS

## Purpose

Define agent behavior, constraints, and workspace rules.

## Instructions

- Follow the coding style established in this repository.
- Run verification commands before considering work complete.
- Do not modify files outside the project scope.

## Verification

```bash
uv run ruff check .
uv run ty check src
uv run pytest tests/ -q
```

## Constraints

- Do not commit or push without explicit approval.
- Do not delete or overwrite existing files without confirmation.
- Preserve existing comments and docstrings.

## Safety Rules

- Do not run destructive commands without confirmation.
- Prefer previewing changes before applying them.
- Keep changes minimal and targeted.
"""

# ── Catalog singleton ─────────────────────────────────────────────────────────────

CATALOG: list[TemplateEntry] = _build_catalog()


def templates_for_category(category_id: str) -> list[TemplateEntry]:
    return [t for t in CATALOG if t.category == category_id]


def template_by_id(template_id: str) -> TemplateEntry | None:
    for t in CATALOG:
        if t.id == template_id:
            return t
    return None


# ── User edits store ──────────────────────────────────────────────────────────────



class UserTemplateStore:
    """Persists user edits to templates as a JSON file, with auto-backups."""

    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self._edits: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            try:
                self._edits = json.loads(
                    self.storage_path.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, OSError):
                self._edits = {}

    def save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(self._edits, indent=2, ensure_ascii=False) + "\n"
        self.storage_path.write_text(content, encoding="utf-8")
        self._backup(content)

    def _backup(self, content: str) -> None:
        import time

        from .paths import backups_root
        backups_dir = backups_root()
        backups_dir.mkdir(parents=True, exist_ok=True)

        timestamp = int(time.time())
        backup_path = backups_dir / f"user_templates_{timestamp}.json"
        backup_path.write_text(content, encoding="utf-8")

        # Keep only the 5 most recent backups
        backups = sorted(backups_dir.glob("user_templates_*.json"))
        for old_backup in backups[:-5]:
            try:
                old_backup.unlink()
            except OSError:
                pass

    def get_content(self, template_id: str) -> str:
        """Return user-edited content, or the default if not edited."""
        if template_id in self._edits:
            return self._edits[template_id]
        entry = template_by_id(template_id)
        return entry.default_content if entry else ""

    def set_content(self, template_id: str, content: str) -> None:
        self._edits[template_id] = content
        self.save()

    def reset_to_default(self, template_id: str) -> None:
        self._edits.pop(template_id, None)
        self.save()

    def is_edited(self, template_id: str) -> bool:
        return template_id in self._edits


@dataclass
class ExportPreset:
    name: str
    template_ids: list[str]
    destination: str
    use_hidden: bool


class ExportPresetStore:
    """Persists named export presets as a JSON file."""

    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self.presets: dict[str, ExportPreset] = {}
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                for name, p in data.items():
                    self.presets[name] = ExportPreset(
                        name=name,
                        template_ids=p.get("template_ids", []),
                        destination=p.get("destination", ""),
                        use_hidden=p.get("use_hidden", False),
                    )
            except (json.JSONDecodeError, OSError):
                self.presets = {}

    def save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            name: {
                "template_ids": p.template_ids,
                "destination": p.destination,
                "use_hidden": p.use_hidden,
            }
            for name, p in self.presets.items()
        }
        self.storage_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def save_preset(
        self, name: str, template_ids: list[str], destination: str, use_hidden: bool
    ) -> None:
        self.presets[name] = ExportPreset(name, template_ids, destination, use_hidden)
        self.save()

    def get_preset(self, name: str) -> ExportPreset | None:
        return self.presets.get(name)

    def get_preset_names(self) -> list[str]:
        return sorted(self.presets.keys())



# ══════════════════════════════════════════════════════════════════════════════════
# Default template content
# ══════════════════════════════════════════════════════════════════════════════════

_CONFIG_README = """\
# Config

Central configuration files for the workspace.
"""

_SCHEMAS_README = """\
# Schemas

Data schemas and validation rules for the project.
"""

_SCRIPTS_README = """\
# Scripts

Utility scripts for automation, deployment, and maintenance.
"""

_SRC_README = """\
# Source

Main source code directory.
"""

_TESTS_README = """\
# Tests

Unit, integration, and end-to-end tests.
"""

_MCP_CONFIGS_README = """\
# MCP Configs

Model Context Protocol (MCP) server configurations.
"""

_RESEARCH_README = """\
# Research

Research notes, experiments, analysis, and architecture exploration.
"""

_RULES_RULES = """\
# Rules

Global project rules, coding standards, and enforcement policies.
"""

