# src/eclipse/storage.py
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from .models import LibraryItem, Metadata, RenderTarget, Requirements


# ── Type directory mapping ────────────────────────────────────────────────────────

TYPE_DIRS: dict[str, str] = {
    "agent":      "agents",
    "asset":      "assets",
    "bundle":     "bundles",
    "skill":      "skills",
    "mcp_server": "mcps",
    "doc":        "docs",
    "repository": "repositories",
    "rule":       "rules",
    "workflow":   "workflows",
}


# ── Low-level manifest serialization ─────────────────────────────────────────────

def load_manifest(path: Path) -> LibraryItem:
    """Load a single manifest.json into a LibraryItem."""
    raw = json.loads(path.read_text(encoding="utf-8"))

    renders = [
        RenderTarget(**r) for r in raw.get("renders", [])
    ]

    req_raw = raw.get("requirements", {})
    requirements = Requirements(
        commands=req_raw.get("commands", []),
        env_vars=req_raw.get("env_vars", []),
    )

    meta_raw = raw.get("metadata", {})
    metadata = Metadata(
        author=meta_raw.get("author", ""),
        created_at=meta_raw.get("created_at", datetime.now(UTC).isoformat()),
        updated_at=meta_raw.get("updated_at", datetime.now(UTC).isoformat()),
    )

    return LibraryItem(
        id=raw["id"],
        type=raw["type"],
        name=raw["name"],
        version=raw.get("version", "1.0.0"),
        description=raw.get("description", ""),
        tags=raw.get("tags", []),
        scope=raw.get("scope", "workspace"),
        targets=raw.get("targets", []),
        renders=renders,
        requirements=requirements,
        metadata=metadata,
        root_dir=path.parent,
        data=raw.get("data", {}),
    )


def save_manifest(item: LibraryItem, path: Path) -> None:
    """Serialize a LibraryItem back to manifest.json atomically."""
    payload = asdict(item)

    # Remove runtime-only field
    payload.pop("root_dir", None)

    # Update the timestamp on every save
    if "metadata" in payload:
        payload["metadata"]["updated_at"] = datetime.now(UTC).isoformat()

    # Atomic write pattern: Write to .tmp file then rename
    tmp_path = path.with_suffix(".tmp")
    try:
        tmp_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(path)
    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink()
        raise OSError(f"Failed to save manifest atomically: {e}") from e


# ── Library scanning ──────────────────────────────────────────────────────────────

def scan_library(library_root: Path) -> list[LibraryItem]:
    """Walk the entire library directory tree and load every manifest.json found."""
    import os
    import sys

    items: list[LibraryItem] = []

    for dirpath, dirnames, filenames in os.walk(library_root):
        dirnames[:] = sorted(dirnames, key=str.lower)
        if "manifest.json" not in filenames:
            continue

        manifest_path = Path(dirpath) / "manifest.json"
        try:
            item = load_manifest(manifest_path)
            items.append(item)
            dirnames[:] = []
        except Exception as exc:
            print(
                f"WARNING: Could not load manifest at {manifest_path}: {exc}",
                file=sys.stderr,
            )

    return sorted(items, key=lambda item: _library_sort_key(library_root, item))


# ── Item-level operations ─────────────────────────────────────────────────────────

def item_manifest_path(item: LibraryItem) -> Path:
    """Return the manifest.json path for an item. Requires root_dir to be set."""
    if item.root_dir is None:
        raise ValueError(f"Item '{item.id}' has no root_dir — was it loaded from disk?")
    return item.root_dir / "manifest.json"


def save_item(item: LibraryItem) -> None:
    """Save changes to an existing library item's manifest."""
    save_manifest(item, item_manifest_path(item))


def delete_item(item: LibraryItem) -> None:
    """Move an item's folder to the macOS Trash using AppleScript."""
    if item.root_dir is None:
        raise ValueError(f"Item '{item.id}' has no root_dir — cannot delete.")

    if not item.root_dir.exists():
        return

    # Native macOS Move to Trash logic
    import subprocess
    try:
        # Note: POSIX file string should be absolute
        script = f'tell application "Finder" to delete POSIX file "{item.root_dir.absolute()}"'
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise OSError(f"Failed to move {item.id} to Trash: {e.stderr.decode().strip()}") from e


def rename_item_dir(item: LibraryItem, new_id: str, library_root: Path) -> Path:
    """Rename an item's folder and update its id in the manifest."""
    if item.root_dir is None:
        raise ValueError(f"Item '{item.id}' has no root_dir.")

    type_dir = TYPE_DIRS.get(item.type, item.type + "s")
    new_dir = library_root / type_dir / new_id

    if new_dir.exists():
        raise FileExistsError(f"An item already exists at: {new_dir}")

    item.root_dir.rename(new_dir)
    item.root_dir = new_dir
    item.id = new_id
    save_item(item)

    return new_dir


def _library_sort_key(library_root: Path, item: LibraryItem) -> tuple[str, ...]:
    if item.root_dir is None:
        return (item.type, item.name.lower())

    try:
        relative_path = item.root_dir.relative_to(library_root)
    except ValueError:
        return (item.type, item.name.lower())

    return tuple(part.lower() for part in relative_path.parts)
