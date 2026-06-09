# src/eclipse/importers/save_to_library.py
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import cast

from ..models import ItemType, LibraryItem, Metadata, Requirements
from ..storage import TYPE_DIRS, save_manifest


MCP_SOURCE_NAMES = ("server.json", "mcp.json", "mcp.md", "mcp.txt")
README_NAMES = ("AGENTS.md", "CLAUDE.md", "README.md")


def slugify(text: str) -> str:
    """Convert arbitrary text into a filesystem-safe and Eclipse-safe ID slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s._-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    text = re.sub(r"^[^a-z0-9]+", "", text)
    return text if text else "unnamed-item"


def save_detected_to_library(
    detected_item: tuple[str, str, Path],
    library_root: Path,
) -> Path:
    kind, name, source_path = detected_item
    return save_classified_to_library(kind, name, source_path, library_root)


def save_classified_to_library(
    kind: str,
    name: str,
    source_path: Path,
    library_root: Path,
) -> Path:
    """Persist a classified file or folder into the organized library.

    Folder imports keep their internal structure intact. The manifest records
    the canonical entry/source file needed by previews and exports.
    """
    source_path = source_path.resolve()
    item_id = slugify(name)
    dest_root, item_id = _next_destination(library_root, kind, item_id)
    dest_root.mkdir(parents=True)

    data = _copy_source(kind, source_path, dest_root)

    item = LibraryItem(
        id=item_id,
        type=cast(ItemType, kind),
        name=name,
        targets=["claude-code", "codex", "cursor", "opencode", "windsurf"],
        metadata=Metadata(),
        requirements=Requirements(),
        data=data,
    )

    save_manifest(item, dest_root / "manifest.json")
    return dest_root


def import_name_for_path(path: Path) -> str:
    path = path.resolve()
    if path.is_dir():
        return path.name
    return path.stem


def _next_destination(library_root: Path, kind: str, item_id: str) -> tuple[Path, str]:
    type_dir = TYPE_DIRS.get(kind, f"{kind}s")
    base_id = item_id
    dest_root = library_root / type_dir / item_id
    counter = 1

    while dest_root.exists():
        counter += 1
        item_id = f"{base_id}-{counter}"
        dest_root = library_root / type_dir / item_id

    return dest_root, item_id


def _copy_source(kind: str, source_path: Path, dest_root: Path) -> dict:
    if source_path.is_dir():
        _copy_directory_contents(source_path, dest_root)
    else:
        shutil.copy2(source_path, dest_root / _canonical_file_name(kind, source_path))

    if kind == "agent":
        return {"instructions_file": _first_existing(dest_root, ("instructions.md",)) or ""}

    if kind == "skill":
        return {"entry_file": _first_existing(dest_root, ("SKILL.md",)) or "SKILL.md"}

    if kind == "mcp_server":
        return _mcp_data(dest_root)

    if kind in {"doc", "rule", "workflow"}:
        return {"content_file": _content_file_for(kind, dest_root)}

    return {"source_folder": "."}


def _copy_directory_contents(source_path: Path, dest_root: Path) -> None:
    for child in sorted(source_path.iterdir(), key=lambda path: path.name.lower()):
        destination = dest_root / child.name
        if child.is_dir():
            shutil.copytree(child, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(child, destination)


def _canonical_file_name(kind: str, source_path: Path) -> str:
    if kind == "agent":
        return "instructions.md"
    if kind == "skill":
        return "SKILL.md"
    if kind == "mcp_server":
        return source_path.name
    if kind == "workflow":
        return "workflow.md"
    if kind == "rule":
        return "body.md"
    if kind == "doc" and source_path.name not in README_NAMES:
        return "body.md"
    if source_path.name in README_NAMES:
        return source_path.name
    return source_path.name


def _mcp_data(dest_root: Path) -> dict:
    source_file = _first_existing(dest_root, MCP_SOURCE_NAMES)
    if source_file is None:
        source_file = _first_mcp_like_file(dest_root) or "mcp.txt"

    data = {"source_file": source_file, "transport": "stdio"}
    source_path = dest_root / source_file
    if source_path.suffix == ".json":
        data.update(_read_mcp_json(source_path))

    return data


def _read_mcp_json(path: Path) -> dict:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    if not isinstance(raw, dict):
        return {}

    return {
        "command": raw.get("command", ""),
        "args": raw.get("args", []),
        "env": raw.get("env", {}),
        "transport": raw.get("transport", "stdio"),
    }


def _content_file_for(kind: str, dest_root: Path) -> str:
    if kind == "doc":
        return _first_existing(dest_root, README_NAMES) or "body.md"
    if kind == "workflow":
        return _first_existing(dest_root, ("workflow.md",)) or "workflow.md"
    return _first_existing(dest_root, ("body.md",)) or "body.md"


def _first_existing(dest_root: Path, names: tuple[str, ...]) -> str | None:
    for name in names:
        if (dest_root / name).exists():
            return name
    return None


def _first_mcp_like_file(dest_root: Path) -> str | None:
    files = sorted((path for path in dest_root.rglob("*") if path.is_file()), key=lambda p: str(p).lower())
    for path in files:
        if path.name in MCP_SOURCE_NAMES:
            return str(path.relative_to(dest_root))
    return None
