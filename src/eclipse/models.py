# src/eclipse/models.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal


# ── Type aliases ─────────────────────────────────────────────────────────────────

ItemType = Literal[
    "agent",
    "skill",
    "mcp_server",
    "doc",
    "rule",
    "workflow",
    "bundle",
    "repository",
    "asset",
]

ScopeType = Literal[
    "global",
    "project",
    "personal",
    "workspace",
]

TargetType = Literal[
    "claude-code",
    "codex",
    "cursor",
    "windsurf",
    "opencode",
]

RenderAsType = Literal[
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "agent_file",
    "cursor_rule",
    "windsurf_workflow",
    "windsurf_rule",
    "windsurf_memory",
    "mcp_config_fragment",
    "codex_config_fragment",
    "rule_file",
    "workflow_file",
    "skill_bundle",
]

# ── Leaf dataclasses ─────────────────────────────────────────────────────────────

@dataclass(slots=True)
class RenderTarget:
    """Describes how a library item should be rendered for a specific tool target."""
    target: TargetType | Literal["all"]
    render_as: RenderAsType
    output_path: str | None = None   # Optional override for the output filename/path


@dataclass(slots=True)
class Requirements:
    """Tools and environment variables this item depends on."""
    commands: list[str] = field(default_factory=list)   # e.g. ["python3", "uv", "ruff"]
    env_vars: list[str] = field(default_factory=list)   # e.g. ["GITHUB_TOKEN"]


@dataclass(slots=True)
class Metadata:
    """Authorship and timestamp tracking."""
    author: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


# ── Primary item dataclass ────────────────────────────────────────────────────────

@dataclass(slots=True)
class LibraryItem:
    """The canonical neutral representation of any item in the Eclipse library.

    This is the single source of truth that flows through:
      storage.py  →  validators.py  →  render.py  →  exporters/*

    Fields
    ------
    id          : URL-safe slug, unique within the library (e.g. "python-bug-fixer")
    type        : One of the seven canonical item types
    name        : Human-readable display name
    version     : Semver string, default "1.0.0"
    description : Short one-liner shown in the library list
    tags        : Free-form labels for filtering/search
    scope       : How broadly this item applies
    targets     : Which tool targets this item can be exported to
    renders     : Explicit render mappings (target → render_as)
    requirements: Commands and env vars needed at runtime
    metadata    : Author and timestamps
    root_dir    : Absolute path to this item's folder on disk (set by storage.py)
    data        : Type-specific payload dict, passed to Jinja2 templates
    """

    # Required fields (no defaults)
    id: str
    type: ItemType
    name: str

    # Optional with defaults
    version: str = "1.0.0"
    description: str = ""
    tags: list[str] = field(default_factory=list)
    scope: ScopeType = "workspace"
    targets: list[TargetType] = field(default_factory=list)
    renders: list[RenderTarget] = field(default_factory=list)
    requirements: Requirements = field(default_factory=Requirements)
    metadata: Metadata = field(default_factory=Metadata)

    # Runtime-only: set by storage.py, not serialized to JSON
    root_dir: Path | None = None

    # Type-specific payload: varies by item type (see section 6)
    data: dict[str, Any] = field(default_factory=dict)


# ── Import/scanner dataclasses ────────────────────────────────────────────────────

@dataclass(slots=True)
class DetectedItem:
    """A candidate item found during a scan of a local folder or GitHub clone.

    Not yet saved to the library — just detected.
    """
    kind: str           # Matches ItemType values (e.g. "skill", "agent", "doc")
    name: str           # Display name derived from filename or folder name
    source_path: Path   # Absolute path to the source file or folder
    notes: list[str] = field(default_factory=list)  # Human-readable detection notes


@dataclass(slots=True)
class ImportResult:
    """The result of scanning a local path or a GitHub clone.

    Contains zero or more DetectedItems and any warnings.
    """
    source_label: str           # Human-readable source description (path or URL)
    working_dir: Path           # The directory that was scanned
    detected_items: list[DetectedItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
