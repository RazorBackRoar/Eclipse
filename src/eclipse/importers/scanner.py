# src/agentbox/importers/scanner.py
from __future__ import annotations

import json
from pathlib import Path

from .base import DetectedItem, ImportResult


def _is_under_named_dir(path: Path, dirname: str) -> bool:
    """Check if a path contains a specific directory name anywhere in its parts."""
    return dirname in path.parts


def _looks_like_mcp_json(path: Path) -> bool:
    """Heuristic: does this JSON file look like an MCP server definition?"""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False

    if not isinstance(raw, dict):
        return False

    keys = set(raw.keys())
    if {"command", "args"} & keys:
        return True
    if raw.get("transport") in {"stdio", "sse", "streamable_http", "http"}:
        return True

    return False


def _looks_like_mcp_text(path: Path) -> bool:
    return path.name in {"mcp.txt", "mcp.md"}


def scan_path(root: Path) -> ImportResult:
    """Scan a directory tree and classify supported items.

    Optimized to skip large junk directories early.
    """
    if root.is_file():
        root = root.parent

    result = ImportResult(source_label=str(root), working_dir=root)
    seen: set[tuple[str, str]] = set()

    # Skip list for early pruning
    junk_dirs = {
        ".git", "node_modules", ".venv", ".env", "venv", "env",
        "__pycache__", ".pytest_cache", ".tox", ".nox", "htmlcov",
        ".idea", ".vscode", ".zed",
        ".next", ".nuxt", ".docusaurus", ".cache",
        "dist", "build", "out", "target", "bin", "obj",
        ".DS_Store", "Thumbs.db"
    }

    # Use a work list or os.walk to prune directories efficiently
    import os
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune junk_dirs in-place to prevent os.walk from descending into them
        dirnames[:] = [d for d in dirnames if d not in junk_dirs]

        current_dir = Path(dirpath)

        # ── Directory-level checks ──────────────────────────────────────────
        # Check if this folder itself looks like an agent (has instructions.md)
        if "instructions.md" in filenames and "manifest.json" not in filenames:
            key = ("agent", dirpath)
            if key not in seen:
                seen.add(key)
                result.detected_items.append(
                    DetectedItem(
                        kind="agent",
                        name=current_dir.name,
                        source_path=current_dir,
                        notes=["Detected agent folder (instructions.md found)"],
                    )
                )

        # ── File-level checks ───────────────────────────────────────────────
        for fname in filenames:
            path = current_dir / fname

            if fname == "SKILL.md":
                key = ("skill", dirpath)
                if key not in seen:
                    seen.add(key)
                    result.detected_items.append(
                        DetectedItem(
                            kind="skill",
                            name=current_dir.name,
                            source_path=current_dir,
                            notes=["Detected SKILL.md folder"],
                        )
                    )

            elif fname == "AGENTS.md":
                result.detected_items.append(
                    DetectedItem(kind="doc", name="AGENTS", source_path=path)
                )
            elif fname == "CLAUDE.md":
                result.detected_items.append(
                    DetectedItem(kind="doc", name="CLAUDE", source_path=path)
                )
            elif fname == "README.md" and current_dir == root: # Only root README
                result.detected_items.append(
                    DetectedItem(kind="doc", name="README", source_path=path)
                )

            elif fname.endswith(".mdc") and ".cursor" in path.parts:
                result.detected_items.append(
                    DetectedItem(kind="rule", name=path.stem, source_path=path)
                )

            elif (fname.endswith(".md")
                    and ".windsurf" in path.parts
                    and "workflows" in path.parts):
                result.detected_items.append(
                    DetectedItem(kind="workflow", name=path.stem, source_path=path)
                )

            elif fname.endswith(".json") and _looks_like_mcp_json(path):
                result.detected_items.append(
                    DetectedItem(
                        kind="mcp_server",
                        name=path.stem,
                        source_path=path,
                        notes=["Detected MCP server (JSON)"],
                    )
                )
            elif _looks_like_mcp_text(path):
                result.detected_items.append(
                    DetectedItem(
                        kind="mcp_server",
                        name=current_dir.name,
                        source_path=path,
                        notes=[f"Detected MCP source ({fname})"],
                    )
                )

    if not result.detected_items:
        result.warnings.append("No supported items detected in the scanned content.")

    result.detected_items.sort(key=lambda item: (str(item.source_path).lower(), item.kind, item.name.lower()))
    return result
