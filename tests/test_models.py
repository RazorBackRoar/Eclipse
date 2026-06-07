from __future__ import annotations

from pathlib import Path

from eclipse.models import (
    DetectedItem,
    ImportResult,
    LibraryItem,
    Metadata,
    RenderTarget,
    Requirements,
)


def test_library_item_required_fields_only() -> None:
    item = LibraryItem(id="my-item", type="agent", name="My Item")
    assert item.id == "my-item"
    assert item.type == "agent"
    assert item.name == "My Item"


def test_library_item_defaults() -> None:
    item = LibraryItem(id="x", type="skill", name="X")
    assert item.version == "1.0.0"
    assert item.description == ""
    assert item.tags == []
    assert item.scope == "workspace"
    assert item.targets == []
    assert item.renders == []
    assert item.root_dir is None
    assert item.data == {}


def test_library_item_requirements_default() -> None:
    item = LibraryItem(id="x", type="doc", name="X")
    assert item.requirements.commands == []
    assert item.requirements.env_vars == []


def test_library_item_metadata_default_timestamps() -> None:
    item = LibraryItem(id="x", type="doc", name="X")
    assert item.metadata.author == ""
    assert item.metadata.created_at
    assert item.metadata.updated_at


def test_library_item_custom_data() -> None:
    item = LibraryItem(
        id="my-agent",
        type="agent",
        name="Agent",
        data={"instructions_file": "agent.md"},
    )
    assert item.data["instructions_file"] == "agent.md"


def test_render_target_fields() -> None:
    rt = RenderTarget(target="claude-code", render_as="CLAUDE.md")
    assert rt.target == "claude-code"
    assert rt.render_as == "CLAUDE.md"
    assert rt.output_path is None


def test_render_target_with_output_path() -> None:
    rt = RenderTarget(target="codex", render_as="AGENTS.md", output_path="subdir/AGENTS.md")
    assert rt.output_path == "subdir/AGENTS.md"


def test_requirements_defaults() -> None:
    req = Requirements()
    assert req.commands == []
    assert req.env_vars == []


def test_requirements_populated() -> None:
    req = Requirements(commands=["python3", "uv"], env_vars=["API_KEY"])
    assert "python3" in req.commands
    assert "API_KEY" in req.env_vars


def test_detected_item_fields() -> None:
    src = Path("/some/path/skill-dir")
    di = DetectedItem(kind="skill", name="my-skill", source_path=src)
    assert di.kind == "skill"
    assert di.name == "my-skill"
    assert di.source_path == src
    assert di.notes == []


def test_detected_item_with_notes() -> None:
    src = Path("/a/b")
    di = DetectedItem(kind="agent", name="bot", source_path=src, notes=["Found instructions.md"])
    assert di.notes == ["Found instructions.md"]


def test_import_result_defaults() -> None:
    wd = Path("/workspace")
    ir = ImportResult(source_label="local", working_dir=wd)
    assert ir.source_label == "local"
    assert ir.working_dir == wd
    assert ir.detected_items == []
    assert ir.warnings == []


def test_import_result_with_items() -> None:
    wd = Path("/workspace")
    item = DetectedItem(kind="doc", name="AGENTS", source_path=Path("/workspace/AGENTS.md"))
    ir = ImportResult(
        source_label="local",
        working_dir=wd,
        detected_items=[item],
        warnings=["minor warning"],
    )
    assert len(ir.detected_items) == 1
    assert len(ir.warnings) == 1


def test_library_item_with_render_targets() -> None:
    renders = [
        RenderTarget(target="claude-code", render_as="CLAUDE.md"),
        RenderTarget(target="codex", render_as="AGENTS.md"),
    ]
    item = LibraryItem(id="x", type="doc", name="X", renders=renders)
    assert len(item.renders) == 2
    assert item.renders[0].target == "claude-code"
