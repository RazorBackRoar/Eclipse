from __future__ import annotations

import json
from pathlib import Path

from eclipse.importers.scanner import _looks_like_mcp_json, scan_path


# ── _looks_like_mcp_json ──────────────────────────────────────────────────────────

def test_looks_like_mcp_json_command_and_args(tmp_path: Path) -> None:
    p = tmp_path / "server.json"
    p.write_text(json.dumps({"command": "python", "args": ["-m", "myserver"]}), encoding="utf-8")
    assert _looks_like_mcp_json(p) is True


def test_looks_like_mcp_json_transport_stdio(tmp_path: Path) -> None:
    p = tmp_path / "server.json"
    p.write_text(json.dumps({"transport": "stdio"}), encoding="utf-8")
    assert _looks_like_mcp_json(p) is True


def test_looks_like_mcp_json_transport_sse(tmp_path: Path) -> None:
    p = tmp_path / "server.json"
    p.write_text(json.dumps({"transport": "sse", "url": "http://localhost"}), encoding="utf-8")
    assert _looks_like_mcp_json(p) is True


def test_looks_like_mcp_json_not_mcp(tmp_path: Path) -> None:
    p = tmp_path / "config.json"
    p.write_text(json.dumps({"name": "my-app", "version": "1.0"}), encoding="utf-8")
    assert _looks_like_mcp_json(p) is False


def test_looks_like_mcp_json_invalid_json(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("not json", encoding="utf-8")
    assert _looks_like_mcp_json(p) is False


def test_looks_like_mcp_json_array(tmp_path: Path) -> None:
    p = tmp_path / "array.json"
    p.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    assert _looks_like_mcp_json(p) is False


# ── scan_path: file input converts to parent ──────────────────────────────────────

def test_scan_path_file_input_uses_parent(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("# Project", encoding="utf-8")
    dummy_file = tmp_path / "CLAUDE.md"
    result = scan_path(dummy_file)
    assert result.working_dir == tmp_path


# ── scan_path: empty directory ────────────────────────────────────────────────────

def test_scan_path_empty_dir_returns_warning(tmp_path: Path) -> None:
    result = scan_path(tmp_path)
    assert result.detected_items == []
    assert len(result.warnings) > 0
    assert any("No supported items" in w for w in result.warnings)


# ── scan_path: agent detection ────────────────────────────────────────────────────

def test_scan_path_detects_agent_folder(tmp_path: Path) -> None:
    agent_dir = tmp_path / "my-agent"
    agent_dir.mkdir()
    (agent_dir / "instructions.md").write_text("# Instructions", encoding="utf-8")

    result = scan_path(tmp_path)
    kinds = [item.kind for item in result.detected_items]
    assert "agent" in kinds


def test_scan_path_agent_has_instructions_note(tmp_path: Path) -> None:
    agent_dir = tmp_path / "bot"
    agent_dir.mkdir()
    (agent_dir / "instructions.md").write_text("content", encoding="utf-8")

    result = scan_path(tmp_path)
    agent_items = [i for i in result.detected_items if i.kind == "agent"]
    assert len(agent_items) == 1
    assert any("instructions.md" in n for n in agent_items[0].notes)


def test_scan_path_agent_not_detected_if_manifest_exists(tmp_path: Path) -> None:
    agent_dir = tmp_path / "has-manifest"
    agent_dir.mkdir()
    (agent_dir / "instructions.md").write_text("content", encoding="utf-8")
    (agent_dir / "manifest.json").write_text("{}", encoding="utf-8")

    result = scan_path(tmp_path)
    kinds = [item.kind for item in result.detected_items]
    assert "agent" not in kinds


# ── scan_path: SKILL.md detection ────────────────────────────────────────────────

def test_scan_path_detects_skill_folder(tmp_path: Path) -> None:
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Skill", encoding="utf-8")

    result = scan_path(tmp_path)
    kinds = [item.kind for item in result.detected_items]
    assert "skill" in kinds


def test_scan_path_skill_deduplicated(tmp_path: Path) -> None:
    skill_dir = tmp_path / "unique-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Skill", encoding="utf-8")

    result = scan_path(tmp_path)
    skill_items = [i for i in result.detected_items if i.kind == "skill"]
    assert len(skill_items) == 1


# ── scan_path: doc detection ──────────────────────────────────────────────────────

def test_scan_path_detects_agents_md(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# Agents", encoding="utf-8")
    result = scan_path(tmp_path)
    docs = [i for i in result.detected_items if i.kind == "doc" and i.name == "AGENTS"]
    assert len(docs) == 1


def test_scan_path_detects_claude_md(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("# Claude", encoding="utf-8")
    result = scan_path(tmp_path)
    docs = [i for i in result.detected_items if i.kind == "doc" and i.name == "CLAUDE"]
    assert len(docs) == 1


def test_scan_path_detects_root_readme(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Readme", encoding="utf-8")
    result = scan_path(tmp_path)
    docs = [i for i in result.detected_items if i.kind == "doc" and i.name == "README"]
    assert len(docs) == 1


def test_scan_path_does_not_detect_non_root_readme(tmp_path: Path) -> None:
    subdir = tmp_path / "subproject"
    subdir.mkdir()
    (subdir / "README.md").write_text("# Sub Readme", encoding="utf-8")
    result = scan_path(tmp_path)
    # Should not find sub-README as a doc
    readme_items = [i for i in result.detected_items if i.name == "README"]
    assert len(readme_items) == 0


# ── scan_path: cursor .mdc rule detection ────────────────────────────────────────

def test_scan_path_detects_cursor_mdc_rule(tmp_path: Path) -> None:
    cursor_rules = tmp_path / ".cursor" / "rules"
    cursor_rules.mkdir(parents=True)
    (cursor_rules / "my-rule.mdc").write_text("rule content", encoding="utf-8")
    result = scan_path(tmp_path)
    rules = [i for i in result.detected_items if i.kind == "rule"]
    assert len(rules) == 1
    assert rules[0].name == "my-rule"


def test_scan_path_mdc_outside_cursor_not_detected(tmp_path: Path) -> None:
    (tmp_path / "some-rule.mdc").write_text("rule", encoding="utf-8")
    result = scan_path(tmp_path)
    rules = [i for i in result.detected_items if i.kind == "rule"]
    assert len(rules) == 0


# ── scan_path: windsurf workflow detection ────────────────────────────────────────

def test_scan_path_detects_windsurf_workflow(tmp_path: Path) -> None:
    wf_dir = tmp_path / ".windsurf" / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "deploy.md").write_text("# Deploy workflow", encoding="utf-8")
    result = scan_path(tmp_path)
    workflows = [i for i in result.detected_items if i.kind == "workflow"]
    assert len(workflows) == 1
    assert workflows[0].name == "deploy"


def test_scan_path_windsurf_md_not_in_workflows_not_detected(tmp_path: Path) -> None:
    ws_dir = tmp_path / ".windsurf"
    ws_dir.mkdir()
    (ws_dir / "rules.md").write_text("rules", encoding="utf-8")
    result = scan_path(tmp_path)
    workflows = [i for i in result.detected_items if i.kind == "workflow"]
    assert len(workflows) == 0


# ── scan_path: MCP server detection ──────────────────────────────────────────────

def test_scan_path_detects_mcp_server_json(tmp_path: Path) -> None:
    mcp_file = tmp_path / "myserver.json"
    mcp_file.write_text(
        json.dumps({"command": "python", "args": ["-m", "mcp"]}), encoding="utf-8"
    )
    result = scan_path(tmp_path)
    mcps = [i for i in result.detected_items if i.kind == "mcp_server"]
    assert len(mcps) == 1
    assert mcps[0].name == "myserver"


def test_scan_path_detects_mcp_txt(tmp_path: Path) -> None:
    (tmp_path / "mcp.txt").write_text("mcp config", encoding="utf-8")
    result = scan_path(tmp_path)
    mcps = [i for i in result.detected_items if i.kind == "mcp_server"]
    assert len(mcps) == 1


def test_scan_path_detects_mcp_md(tmp_path: Path) -> None:
    (tmp_path / "mcp.md").write_text("# MCP config", encoding="utf-8")
    result = scan_path(tmp_path)
    mcps = [i for i in result.detected_items if i.kind == "mcp_server"]
    assert len(mcps) == 1


# ── scan_path: junk directory pruning ────────────────────────────────────────────

def test_scan_path_skips_git_directory(tmp_path: Path) -> None:
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "AGENTS.md").write_text("# Agents", encoding="utf-8")
    result = scan_path(tmp_path)
    # No items should be detected from inside .git
    assert result.detected_items == []


def test_scan_path_skips_node_modules(tmp_path: Path) -> None:
    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    agent_dir = node_modules / "fake-agent"
    agent_dir.mkdir()
    (agent_dir / "instructions.md").write_text("content", encoding="utf-8")
    result = scan_path(tmp_path)
    assert result.detected_items == []


def test_scan_path_skips_venv(tmp_path: Path) -> None:
    venv = tmp_path / ".venv"
    venv.mkdir()
    (venv / "SKILL.md").write_text("# Skill", encoding="utf-8")
    result = scan_path(tmp_path)
    assert result.detected_items == []


# ── scan_path: result sorting ─────────────────────────────────────────────────────

def test_scan_path_results_are_sorted(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("# Claude", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# Agents", encoding="utf-8")
    result = scan_path(tmp_path)
    paths = [str(item.source_path).lower() for item in result.detected_items]
    assert paths == sorted(paths)


# ── scan_path: source_label ───────────────────────────────────────────────────────

def test_scan_path_source_label_is_root(tmp_path: Path) -> None:
    result = scan_path(tmp_path)
    assert result.source_label == str(tmp_path)
