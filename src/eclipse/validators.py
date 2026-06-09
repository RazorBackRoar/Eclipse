# src/eclipse/validators.py
from __future__ import annotations

import re

from .models import LibraryItem


# ── Constants ─────────────────────────────────────────────────────────────────────

# Valid item id: starts with lowercase letter or digit, then allows a-z 0-9 . _ -
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")

VALID_ITEM_TYPES = frozenset(
    ["agent", "asset", "bundle", "doc", "mcp_server", "repository", "rule", "skill", "workflow"]
)

VALID_TARGETS = frozenset(
    ["claude-code", "codex", "cursor", "windsurf", "opencode", "all"]
)

VALID_RENDER_AS = frozenset([
    "AGENTS.md", "CLAUDE.md", "README.md",
    "agent_file", "cursor_rule", "windsurf_workflow",
    "windsurf_rule", "windsurf_memory", "mcp_config_fragment",
    "codex_config_fragment", "rule_file", "workflow_file", "skill_bundle",
])

# Required data keys per item type
REQUIRED_DATA_KEYS: dict[str, list[str]] = {
    "agent":      ["instructions_file"],
    "asset":      [],
    "bundle":     [],
    "skill":      ["entry_file"],
    "mcp_server": ["source_file"],
    "doc":        ["content_file"],
    "repository": [],
    "rule":       ["content_file"],
    "workflow":   ["content_file"],
}

# ── Single-item validation ────────────────────────────────────────────────────────

def validate_item(item: LibraryItem) -> list[str]:
    """Validate a single LibraryItem."""
    errors: list[str] = []

    # ── ID format ────────────────────────────────────────────────────────────────
    if not item.id:
        errors.append("id cannot be empty")
    elif not _ID_RE.match(item.id):
        errors.append(
            f"Invalid id '{item.id}': must start with a-z or 0-9, "
            f"then allow a-z 0-9 . _ - only"
        )

    # ── Name ─────────────────────────────────────────────────────────────────────
    if not item.name.strip():
        errors.append("name cannot be empty or whitespace-only")

    # ── Type ─────────────────────────────────────────────────────────────────────
    if item.type not in VALID_ITEM_TYPES:
        errors.append(f"Unknown item type: '{item.type}'")

    # ── Targets ──────────────────────────────────────────────────────────────────
    for target in item.targets:
        if target not in VALID_TARGETS:
            errors.append(f"Unknown target: '{target}'")

    # ── Render targets ───────────────────────────────────────────────────────────
    for render in item.renders:
        if render.target not in VALID_TARGETS:
            errors.append(f"Render has unknown target: '{render.target}'")
        if render.render_as not in VALID_RENDER_AS:
            errors.append(f"Render has unknown render_as: '{render.render_as}'")

    # ── Required data keys ───────────────────────────────────────────────────────
    required_keys = REQUIRED_DATA_KEYS.get(item.type, [])
    for key in required_keys:
        if not item.data.get(key):
            errors.append(f"Item type '{item.type}' is missing required data key: '{key}'")

    # ── Sidecar file existence ───────────────────────────────────────────────────
    if item.root_dir is not None:
        errors.extend(_validate_sidecars(item))

    return errors


def _validate_sidecars(item: LibraryItem) -> list[str]:
    """Check that required sidecar files actually exist on disk."""
    errors: list[str] = []
    root = item.root_dir
    assert root is not None  # caller ensures this

    if item.type == "agent":
        instructions_file = item.data.get("instructions_file", "instructions.md")
        path = root / instructions_file
        if not path.exists():
            errors.append(f"Agent sidecar missing: {path}")

    elif item.type == "skill":
        entry_file = item.data.get("entry_file", "SKILL.md")
        path = root / entry_file
        if not path.exists():
            errors.append(f"Skill entry file missing: {path}")

    elif item.type == "mcp_server":
        source_file = item.data.get("source_file", "server.json")
        path = root / source_file
        if not path.exists():
            errors.append(f"MCP server source file missing: {path}")

    elif item.type in ("doc", "rule", "workflow"):
        content_file = item.data.get("content_file", "body.md")
        path = root / content_file
        if not path.exists():
            errors.append(f"{item.type.capitalize()} content file missing: {path}")

    return errors


# ── Library-level validation ──────────────────────────────────────────────────────

def validate_library(items: list[LibraryItem]) -> list[str]:
    """Validate all items in the library together."""
    errors: list[str] = []
    seen_ids: set[str] = set()

    for item in items:
        # Check for duplicate IDs
        if item.id in seen_ids:
            errors.append(f"Duplicate item id: '{item.id}'")
        seen_ids.add(item.id)

        # Run per-item validation
        item_errors = validate_item(item)
        for err in item_errors:
            errors.append(f"[{item.id}] {err}")

    return errors
