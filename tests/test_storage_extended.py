from __future__ import annotations

import json
from pathlib import Path

import pytest

from eclipse.models import LibraryItem
from eclipse.storage import (
    TYPE_DIRS,
    item_manifest_path,
    load_manifest,
    rename_item_dir,
    save_manifest,
    scan_library,
)


# ── Helpers ───────────────────────────────────────────────────────────────────────

def _make_manifest(directory: Path, payload: dict) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _minimal_payload(item_id: str = "test-item", item_type: str = "agent") -> dict:
    return {
        "id": item_id,
        "type": item_type,
        "name": "Test Item",
        "version": "1.0.0",
        "description": "",
        "tags": [],
        "scope": "workspace",
        "targets": [],
        "renders": [],
        "requirements": {"commands": [], "env_vars": []},
        "metadata": {"author": "", "created_at": "2024-01-01T00:00:00+00:00", "updated_at": "2024-01-01T00:00:00+00:00"},
        "data": {},
    }


# ── scan_library ──────────────────────────────────────────────────────────────────

def test_scan_library_empty_dir(tmp_path: Path) -> None:
    assert scan_library(tmp_path) == []


def test_scan_library_finds_single_manifest(tmp_path: Path) -> None:
    _make_manifest(tmp_path / "agents" / "my-agent", _minimal_payload("my-agent", "agent"))
    items = scan_library(tmp_path)
    assert len(items) == 1
    assert items[0].id == "my-agent"


def test_scan_library_finds_multiple_manifests(tmp_path: Path) -> None:
    _make_manifest(tmp_path / "agents" / "agent-a", _minimal_payload("agent-a", "agent"))
    _make_manifest(tmp_path / "skills" / "skill-b", _minimal_payload("skill-b", "skill"))
    _make_manifest(tmp_path / "docs" / "doc-c", _minimal_payload("doc-c", "doc"))
    items = scan_library(tmp_path)
    assert len(items) == 3
    ids = {item.id for item in items}
    assert ids == {"agent-a", "skill-b", "doc-c"}


def test_scan_library_sets_root_dir(tmp_path: Path) -> None:
    item_dir = tmp_path / "agents" / "my-agent"
    _make_manifest(item_dir, _minimal_payload("my-agent"))
    items = scan_library(tmp_path)
    assert items[0].root_dir == item_dir


def test_scan_library_skips_nested_manifest(tmp_path: Path) -> None:
    """When a manifest.json is found, scanning stops descending into its subdirectories."""
    parent_dir = tmp_path / "agents" / "parent"
    _make_manifest(parent_dir, _minimal_payload("parent-item"))
    # Nested manifest inside parent should be ignored
    nested_dir = parent_dir / "nested"
    _make_manifest(nested_dir, _minimal_payload("nested-item"))

    items = scan_library(tmp_path)
    assert len(items) == 1
    assert items[0].id == "parent-item"


def test_scan_library_handles_corrupt_manifest(tmp_path: Path, capsys) -> None:
    bad_dir = tmp_path / "agents" / "bad-agent"
    bad_dir.mkdir(parents=True)
    (bad_dir / "manifest.json").write_text("{ invalid json", encoding="utf-8")

    # Should not raise — just print a warning
    items = scan_library(tmp_path)
    assert items == []
    captured = capsys.readouterr()
    assert "WARNING" in captured.err


def test_scan_library_handles_missing_required_field(tmp_path: Path, capsys) -> None:
    bad_dir = tmp_path / "agents" / "incomplete"
    bad_dir.mkdir(parents=True)
    # Missing "type" field — will raise KeyError in load_manifest
    (bad_dir / "manifest.json").write_text(json.dumps({"id": "x", "name": "X"}), encoding="utf-8")
    items = scan_library(tmp_path)
    assert items == []
    captured = capsys.readouterr()
    assert "WARNING" in captured.err


def test_scan_library_sorts_results(tmp_path: Path) -> None:
    _make_manifest(tmp_path / "agents" / "zz-item", _minimal_payload("zz-item"))
    _make_manifest(tmp_path / "agents" / "aa-item", _minimal_payload("aa-item"))
    items = scan_library(tmp_path)
    # Sorted by path components, which sorts alphabetically
    assert items[0].id == "aa-item"
    assert items[1].id == "zz-item"


def test_scan_library_loads_full_manifest_fields(tmp_path: Path) -> None:
    payload = _minimal_payload("full-item", "skill")
    payload.update({
        "version": "2.1.0",
        "description": "A test skill",
        "tags": ["ai", "test"],
        "scope": "global",
        "targets": ["claude-code"],
        "renders": [{"target": "claude-code", "render_as": "CLAUDE.md", "output_path": None}],
        "requirements": {"commands": ["python3"], "env_vars": ["API_KEY"]},
        "data": {"entry_file": "SKILL.md"},
    })
    item_dir = tmp_path / "skills" / "full-item"
    _make_manifest(item_dir, payload)

    items = scan_library(tmp_path)
    assert len(items) == 1
    item = items[0]
    assert item.version == "2.1.0"
    assert item.description == "A test skill"
    assert item.tags == ["ai", "test"]
    assert item.scope == "global"
    assert item.targets == ["claude-code"]
    assert item.renders[0].render_as == "CLAUDE.md"
    assert item.requirements.commands == ["python3"]
    assert item.requirements.env_vars == ["API_KEY"]
    assert item.data["entry_file"] == "SKILL.md"


# ── item_manifest_path ────────────────────────────────────────────────────────────

def test_item_manifest_path_with_root_dir(tmp_path: Path) -> None:
    item = LibraryItem(id="x", type="agent", name="X", root_dir=tmp_path)
    assert item_manifest_path(item) == tmp_path / "manifest.json"


def test_item_manifest_path_without_root_dir_raises() -> None:
    item = LibraryItem(id="x", type="agent", name="X")
    with pytest.raises(ValueError, match="no root_dir"):
        item_manifest_path(item)


# ── rename_item_dir ───────────────────────────────────────────────────────────────

def test_rename_item_dir_succeeds(tmp_path: Path) -> None:
    library_root = tmp_path
    item_dir = library_root / "agents" / "old-name"
    _make_manifest(item_dir, _minimal_payload("old-name", "agent"))
    item = load_manifest(item_dir / "manifest.json")

    new_dir = rename_item_dir(item, "new-name", library_root)

    assert new_dir.exists()
    assert not item_dir.exists()
    assert item.id == "new-name"
    assert item.root_dir == new_dir


def test_rename_item_dir_updates_manifest(tmp_path: Path) -> None:
    library_root = tmp_path
    item_dir = library_root / "agents" / "orig"
    _make_manifest(item_dir, _minimal_payload("orig", "agent"))
    item = load_manifest(item_dir / "manifest.json")

    new_dir = rename_item_dir(item, "renamed", library_root)
    reloaded = load_manifest(new_dir / "manifest.json")
    assert reloaded.id == "renamed"


def test_rename_item_dir_raises_if_collision(tmp_path: Path) -> None:
    library_root = tmp_path
    item_dir = library_root / "agents" / "original"
    conflict_dir = library_root / "agents" / "conflict"
    _make_manifest(item_dir, _minimal_payload("original", "agent"))
    _make_manifest(conflict_dir, _minimal_payload("conflict", "agent"))

    item = load_manifest(item_dir / "manifest.json")
    with pytest.raises(FileExistsError):
        rename_item_dir(item, "conflict", library_root)


def test_rename_item_dir_raises_if_no_root_dir() -> None:
    item = LibraryItem(id="x", type="agent", name="X")
    with pytest.raises(ValueError, match="no root_dir"):
        rename_item_dir(item, "new-name", Path("/tmp"))


# ── TYPE_DIRS mapping ─────────────────────────────────────────────────────────────

def test_type_dirs_covers_all_known_types() -> None:
    expected_types = {"agent", "asset", "bundle", "skill", "mcp_server", "doc", "repository", "rule", "workflow"}
    assert set(TYPE_DIRS.keys()) == expected_types


# ── Atomic write failure recovery ────────────────────────────────────────────────

def test_save_manifest_cleans_up_tmp_on_failure(tmp_path: Path, monkeypatch) -> None:
    """If writing fails mid-way, the .tmp file should be cleaned up."""
    from unittest.mock import patch

    item = LibraryItem(id="x", type="agent", name="X", data={})
    manifest_path = tmp_path / "manifest.json"

    def failing_replace(self, target):
        raise OSError("Simulated disk failure")

    with patch.object(Path, "replace", failing_replace):
        with pytest.raises(OSError, match="Failed to save manifest"):
            save_manifest(item, manifest_path)

    # .tmp file should have been cleaned up
    tmp_file = manifest_path.with_suffix(".tmp")
    assert not tmp_file.exists()
