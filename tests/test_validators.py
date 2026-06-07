from __future__ import annotations

from pathlib import Path

import pytest

from eclipse.models import LibraryItem, RenderTarget
from eclipse.validators import validate_item, validate_library


# ── Helpers ───────────────────────────────────────────────────────────────────────

def _item(**kwargs) -> LibraryItem:
    defaults = {"id": "valid-id", "type": "agent", "name": "Valid Item"}
    defaults.update(kwargs)
    return LibraryItem(**defaults)


# ── ID validation ─────────────────────────────────────────────────────────────────

def test_valid_item_passes() -> None:
    item = _item(type="agent", data={"instructions_file": "instructions.md"})
    assert validate_item(item) == []


def test_empty_id_fails() -> None:
    item = _item(id="")
    errors = validate_item(item)
    assert any("id cannot be empty" in e for e in errors)


def test_id_with_uppercase_fails() -> None:
    item = _item(id="Invalid-ID")
    errors = validate_item(item)
    assert any("Invalid id" in e for e in errors)


def test_id_starting_with_dash_fails() -> None:
    item = _item(id="-starts-with-dash")
    errors = validate_item(item)
    assert any("Invalid id" in e for e in errors)


def test_id_with_valid_special_chars() -> None:
    item = _item(id="my.skill_v2-final", type="skill", data={"entry_file": "SKILL.md"})
    errors = validate_item(item)
    assert not any("Invalid id" in e for e in errors)


def test_id_digits_only() -> None:
    item = _item(id="123", type="doc", data={"content_file": "body.md"})
    errors = validate_item(item)
    assert not any("Invalid id" in e for e in errors)


# ── Name validation ───────────────────────────────────────────────────────────────

def test_empty_name_fails() -> None:
    item = _item(name="")
    errors = validate_item(item)
    assert any("name cannot be empty" in e for e in errors)


def test_whitespace_only_name_fails() -> None:
    item = _item(name="   ")
    errors = validate_item(item)
    assert any("name cannot be empty" in e for e in errors)


# ── Type validation ───────────────────────────────────────────────────────────────

def test_unknown_type_fails() -> None:
    item = _item(type="bogus_type")  # type: ignore[arg-type]
    errors = validate_item(item)
    assert any("Unknown item type" in e for e in errors)


@pytest.mark.parametrize("item_type", [
    "agent", "asset", "bundle", "doc", "mcp_server", "repository", "rule", "skill", "workflow"
])
def test_all_valid_types_pass(item_type: str) -> None:
    data_map = {
        "agent": {"instructions_file": "instructions.md"},
        "skill": {"entry_file": "SKILL.md"},
        "mcp_server": {"source_file": "server.json"},
        "doc": {"content_file": "body.md"},
        "rule": {"content_file": "body.md"},
        "workflow": {"content_file": "body.md"},
    }
    item = _item(type=item_type, data=data_map.get(item_type, {}))  # type: ignore[arg-type]
    errors = validate_item(item)
    assert not any("Unknown item type" in e for e in errors)


# ── Target validation ─────────────────────────────────────────────────────────────

def test_unknown_target_fails() -> None:
    item = _item(targets=["not-a-real-target"])  # type: ignore[list-item]
    errors = validate_item(item)
    assert any("Unknown target" in e for e in errors)


def test_valid_targets_pass() -> None:
    item = _item(
        type="agent",
        data={"instructions_file": "instructions.md"},
        targets=["claude-code", "codex"],
    )
    errors = validate_item(item)
    assert not any("Unknown target" in e for e in errors)


# ── Render target validation ──────────────────────────────────────────────────────

def test_render_with_unknown_target_fails() -> None:
    renders = [RenderTarget(target="nonexistent", render_as="CLAUDE.md")]  # type: ignore[arg-type]
    item = _item(renders=renders)
    errors = validate_item(item)
    assert any("Render has unknown target" in e for e in errors)


def test_render_with_unknown_render_as_fails() -> None:
    renders = [RenderTarget(target="claude-code", render_as="FAKE.txt")]  # type: ignore[arg-type]
    item = _item(renders=renders)
    errors = validate_item(item)
    assert any("Render has unknown render_as" in e for e in errors)


def test_valid_render_passes() -> None:
    renders = [RenderTarget(target="claude-code", render_as="CLAUDE.md")]
    item = _item(
        type="agent",
        data={"instructions_file": "instructions.md"},
        renders=renders,
    )
    errors = validate_item(item)
    assert not any("Render" in e for e in errors)


# ── Required data keys ────────────────────────────────────────────────────────────

def test_agent_missing_instructions_file_fails() -> None:
    item = _item(type="agent", data={})
    errors = validate_item(item)
    assert any("instructions_file" in e for e in errors)


def test_skill_missing_entry_file_fails() -> None:
    item = _item(type="skill", data={})
    errors = validate_item(item)
    assert any("entry_file" in e for e in errors)


def test_mcp_server_missing_source_file_fails() -> None:
    item = _item(type="mcp_server", data={})
    errors = validate_item(item)
    assert any("source_file" in e for e in errors)


def test_doc_missing_content_file_fails() -> None:
    item = _item(type="doc", data={})
    errors = validate_item(item)
    assert any("content_file" in e for e in errors)


def test_bundle_has_no_required_data_keys() -> None:
    item = _item(type="bundle", data={})
    errors = validate_item(item)
    assert not any("missing required data key" in e for e in errors)


# ── Sidecar file validation ───────────────────────────────────────────────────────

def test_agent_sidecar_present_passes(tmp_path: Path) -> None:
    (tmp_path / "instructions.md").write_text("agent instructions", encoding="utf-8")
    item = _item(
        type="agent",
        data={"instructions_file": "instructions.md"},
        root_dir=tmp_path,
    )
    # Manually set root_dir since it's a slot and not in constructor
    object.__setattr__(item, "root_dir", tmp_path)
    errors = validate_item(item)
    assert not any("sidecar" in e.lower() for e in errors)


def test_agent_sidecar_missing_fails(tmp_path: Path) -> None:
    item = LibraryItem(
        id="my-agent",
        type="agent",
        name="Agent",
        data={"instructions_file": "instructions.md"},
        root_dir=tmp_path,
    )
    errors = validate_item(item)
    assert any("Agent sidecar missing" in e for e in errors)


def test_skill_entry_file_missing_fails(tmp_path: Path) -> None:
    item = LibraryItem(
        id="my-skill",
        type="skill",
        name="Skill",
        data={"entry_file": "SKILL.md"},
        root_dir=tmp_path,
    )
    errors = validate_item(item)
    assert any("Skill entry file missing" in e for e in errors)


def test_mcp_source_file_missing_fails(tmp_path: Path) -> None:
    item = LibraryItem(
        id="my-mcp",
        type="mcp_server",
        name="MCP",
        data={"source_file": "server.json"},
        root_dir=tmp_path,
    )
    errors = validate_item(item)
    assert any("MCP server source file missing" in e for e in errors)


def test_doc_content_file_missing_fails(tmp_path: Path) -> None:
    item = LibraryItem(
        id="my-doc",
        type="doc",
        name="Doc",
        data={"content_file": "body.md"},
        root_dir=tmp_path,
    )
    errors = validate_item(item)
    assert any("content file missing" in e.lower() for e in errors)


def test_rule_content_file_missing_fails(tmp_path: Path) -> None:
    item = LibraryItem(
        id="my-rule",
        type="rule",
        name="Rule",
        data={"content_file": "rules.md"},
        root_dir=tmp_path,
    )
    errors = validate_item(item)
    assert any("content file missing" in e.lower() for e in errors)


def test_workflow_content_file_missing_fails(tmp_path: Path) -> None:
    item = LibraryItem(
        id="my-flow",
        type="workflow",
        name="Flow",
        data={"content_file": "flow.md"},
        root_dir=tmp_path,
    )
    errors = validate_item(item)
    assert any("content file missing" in e.lower() for e in errors)


def test_sidecar_not_checked_when_no_root_dir() -> None:
    item = _item(type="agent", data={"instructions_file": "instructions.md"})
    assert item.root_dir is None
    errors = validate_item(item)
    assert not any("sidecar" in e.lower() for e in errors)


# ── Library-level validation ──────────────────────────────────────────────────────

def test_validate_library_no_duplicates() -> None:
    items = [
        _item(id="item-a", type="asset"),
        _item(id="item-b", type="asset"),
    ]
    errors = validate_library(items)
    assert errors == []


def test_validate_library_duplicate_id() -> None:
    items = [
        _item(id="same-id", type="asset"),
        _item(id="same-id", type="asset"),
    ]
    errors = validate_library(items)
    assert any("Duplicate item id: 'same-id'" in e for e in errors)


def test_validate_library_errors_prefixed_with_id() -> None:
    items = [_item(id="bad-item", type="bogus_type")]  # type: ignore[arg-type]
    errors = validate_library(items)
    assert all(e.startswith("[bad-item]") for e in errors)


def test_validate_library_empty_list() -> None:
    assert validate_library([]) == []
