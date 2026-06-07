from __future__ import annotations

from pathlib import Path

from eclipse.safe_export import (
    ExportItem,
    ExportPlan,
    _apply_hidden,
    build_export_plan,
    execute_export,
)


# ── _apply_hidden ─────────────────────────────────────────────────────────────────

def test_apply_hidden_standalone_file_unchanged() -> None:
    assert _apply_hidden("AGENTS.md") == "AGENTS.md"
    assert _apply_hidden("CLAUDE.md") == "CLAUDE.md"


def test_apply_hidden_folder_gets_dot_prefix() -> None:
    assert _apply_hidden("cursor/rules.md") == ".cursor/rules.md"
    assert _apply_hidden("skills/my-skill/SKILL.md") == ".skills/my-skill/SKILL.md"


def test_apply_hidden_already_dotted_unchanged() -> None:
    assert _apply_hidden(".cursor/rules.md") == ".cursor/rules.md"
    assert _apply_hidden(".claude/agents/bot.md") == ".claude/agents/bot.md"


def test_apply_hidden_nested_path() -> None:
    result = _apply_hidden("windsurf/workflows/deploy.md")
    assert result == ".windsurf/workflows/deploy.md"


# ── ExportItem ────────────────────────────────────────────────────────────────────

def test_export_item_no_conflict_diff_lines_empty() -> None:
    item = ExportItem(relative_path="AGENTS.md", content="# Agents\n")
    assert item.diff_lines() == []


def test_export_item_conflict_no_existing_content_diff_empty() -> None:
    item = ExportItem(
        relative_path="AGENTS.md",
        content="# New\n",
        conflict=True,
        existing_content="",
    )
    assert item.diff_lines() == []


def test_export_item_conflict_returns_diff() -> None:
    item = ExportItem(
        relative_path="AGENTS.md",
        content="# New Agents\n\nNew content",
        conflict=True,
        existing_content="# Old Agents\n\nOld content",
    )
    diff = item.diff_lines()
    assert len(diff) > 0
    assert any("---" in line or "+++" in line for line in diff)
    assert any("New content" in line for line in diff)
    assert any("Old content" in line for line in diff)


def test_export_item_default_no_conflict() -> None:
    item = ExportItem(relative_path="test.md", content="content")
    assert item.conflict is False
    assert item.existing_content == ""


# ── ExportPlan ────────────────────────────────────────────────────────────────────

def test_export_plan_has_conflicts_false_when_none(tmp_path: Path) -> None:
    plan = ExportPlan(destination=tmp_path)
    plan.items = [
        ExportItem("a.md", "content-a"),
        ExportItem("b.md", "content-b"),
    ]
    assert plan.has_conflicts is False


def test_export_plan_has_conflicts_true_when_any(tmp_path: Path) -> None:
    plan = ExportPlan(destination=tmp_path)
    plan.items = [
        ExportItem("a.md", "content-a"),
        ExportItem("b.md", "content-b", conflict=True),
    ]
    assert plan.has_conflicts is True


def test_export_plan_conflict_paths(tmp_path: Path) -> None:
    plan = ExportPlan(destination=tmp_path)
    plan.items = [
        ExportItem("good.md", "ok"),
        ExportItem("conflict.md", "new", conflict=True),
    ]
    assert plan.conflict_paths == ["conflict.md"]


def test_export_plan_summary_lines_no_conflicts(tmp_path: Path) -> None:
    plan = ExportPlan(destination=tmp_path, use_hidden=False)
    plan.items = [ExportItem("AGENTS.md", "content")]
    lines = plan.summary_lines()
    assert any("AGENTS.md" in line for line in lines)
    assert any("Mode: normal" in line for line in lines)
    assert any("Files: 1" in line for line in lines)


def test_export_plan_summary_lines_hidden_mode(tmp_path: Path) -> None:
    plan = ExportPlan(destination=tmp_path, use_hidden=True)
    plan.items = []
    lines = plan.summary_lines()
    assert any("Mode: hidden" in line for line in lines)


def test_export_plan_summary_lines_with_conflict(tmp_path: Path) -> None:
    plan = ExportPlan(destination=tmp_path)
    plan.items = [ExportItem("existing.md", "new", conflict=True, existing_content="old")]
    lines = plan.summary_lines()
    assert any("EXISTS" in line for line in lines)
    assert any("Conflicts:" in line for line in lines)


# ── build_export_plan ─────────────────────────────────────────────────────────────

def test_build_export_plan_no_conflicts(tmp_path: Path) -> None:
    files = [
        ("AGENTS.md", "# Agents\n"),
        ("README.md", "# Readme\n"),
    ]
    plan = build_export_plan(tmp_path, files)
    assert plan.destination == tmp_path
    assert len(plan.items) == 2
    assert plan.has_conflicts is False


def test_build_export_plan_detects_existing_file_as_conflict(tmp_path: Path) -> None:
    existing = tmp_path / "AGENTS.md"
    existing.write_text("old content", encoding="utf-8")

    plan = build_export_plan(tmp_path, [("AGENTS.md", "new content")])
    assert plan.has_conflicts is True
    assert plan.items[0].existing_content == "old content"
    assert plan.items[0].content == "new content"


def test_build_export_plan_use_hidden_transforms_paths(tmp_path: Path) -> None:
    files = [("cursor/CURSOR.md", "content")]
    plan = build_export_plan(tmp_path, files, use_hidden=True)
    assert plan.items[0].relative_path == ".cursor/CURSOR.md"


def test_build_export_plan_standalone_file_not_hidden(tmp_path: Path) -> None:
    files = [("AGENTS.md", "content")]
    plan = build_export_plan(tmp_path, files, use_hidden=True)
    # Standalone file should not get the dot prefix
    assert plan.items[0].relative_path == "AGENTS.md"


def test_build_export_plan_conflict_reads_existing_content(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("existing text", encoding="utf-8")
    plan = build_export_plan(tmp_path, [("CLAUDE.md", "new text")])
    assert plan.items[0].existing_content == "existing text"


def test_build_export_plan_empty_files_list(tmp_path: Path) -> None:
    plan = build_export_plan(tmp_path, [])
    assert plan.items == []
    assert plan.has_conflicts is False


def test_build_export_plan_unreadable_existing_file(tmp_path: Path) -> None:
    """build_export_plan handles OSError when reading existing file silently."""
    target = tmp_path / "AGENTS.md"
    target.write_text("content", encoding="utf-8")
    target.chmod(0o000)
    try:
        plan = build_export_plan(tmp_path, [("AGENTS.md", "new")])
        assert plan.has_conflicts is True
        assert plan.items[0].existing_content == ""
    finally:
        target.chmod(0o644)


# ── execute_export ────────────────────────────────────────────────────────────────

def test_execute_export_writes_files(tmp_path: Path) -> None:
    plan = build_export_plan(tmp_path, [("AGENTS.md", "# Agents\n"), ("README.md", "# Readme\n")])
    written = execute_export(plan)
    assert len(written) == 2
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == "# Agents\n"
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "# Readme\n"


def test_execute_export_appends_newline_if_missing(tmp_path: Path) -> None:
    plan = build_export_plan(tmp_path, [("AGENTS.md", "# Agents")])
    execute_export(plan)
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8").endswith("\n")


def test_execute_export_creates_parent_dirs(tmp_path: Path) -> None:
    plan = build_export_plan(tmp_path, [("subdir/nested/file.md", "content")])
    execute_export(plan)
    assert (tmp_path / "subdir" / "nested" / "file.md").exists()


def test_execute_export_skips_conflicts_by_default(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("original", encoding="utf-8")
    plan = build_export_plan(tmp_path, [("AGENTS.md", "new content")])
    written = execute_export(plan, overwrite=False)
    assert written == []
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == "original"


def test_execute_export_overwrites_when_flag_set(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("original", encoding="utf-8")
    plan = build_export_plan(tmp_path, [("AGENTS.md", "new content")])
    written = execute_export(plan, overwrite=True)
    assert len(written) == 1
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == "new content\n"


def test_execute_export_returns_written_paths(tmp_path: Path) -> None:
    plan = build_export_plan(tmp_path, [("output.md", "content")])
    written = execute_export(plan)
    assert written == [tmp_path / "output.md"]


def test_execute_export_empty_plan(tmp_path: Path) -> None:
    plan = build_export_plan(tmp_path, [])
    written = execute_export(plan)
    assert written == []
