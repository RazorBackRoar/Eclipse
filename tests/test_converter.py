from __future__ import annotations

import pytest
from eclipse.converter import (
    FORMATS,
    VALID_CONVERSIONS,
    available_targets,
    can_convert,
    convert,
    detect_format,
    format_label,
)


# ── format_label ──────────────────────────────────────────────────────────────────

def test_format_label_known() -> None:
    assert format_label("claude") == "CLAUDE.md"
    assert format_label("agents") == "AGENTS.md"
    assert format_label("windsurf") == ".windsurfrules"


def test_format_label_unknown_returns_id() -> None:
    assert format_label("does-not-exist") == "does-not-exist"


# ── can_convert ───────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("src,tgt", VALID_CONVERSIONS)
def test_can_convert_all_valid_pairs(src: str, tgt: str) -> None:
    assert can_convert(src, tgt) is True


def test_can_convert_invalid_pair() -> None:
    assert can_convert("claude", "cursor") is False


def test_can_convert_same_format() -> None:
    assert can_convert("claude", "claude") is False


def test_can_convert_unknown_format() -> None:
    assert can_convert("bogus", "agents") is False


# ── available_targets ─────────────────────────────────────────────────────────────

def test_available_targets_from_claude() -> None:
    targets = available_targets("claude")
    assert "agents" in targets
    assert "cursor" not in targets


def test_available_targets_from_agents() -> None:
    targets = available_targets("agents")
    assert "claude" in targets
    assert "cursor" in targets
    assert "gemini" in targets
    assert "opencode" in targets
    assert "windsurf" in targets


def test_available_targets_unknown_format() -> None:
    assert available_targets("bogus") == []


# ── detect_format ─────────────────────────────────────────────────────────────────

def test_detect_format_claude() -> None:
    assert detect_format("# Project Instructions\n\n## Behavior") == "claude"


def test_detect_format_claude_by_keyword() -> None:
    assert detect_format("Claude Code is awesome") == "claude"


def test_detect_format_cursor() -> None:
    assert detect_format("# Cursor Rules\n\nFollow cursor guidelines.") == "cursor"


def test_detect_format_gemini() -> None:
    assert detect_format("# Gemini Instructions\n\nContent here.") == "gemini"


def test_detect_format_opencode() -> None:
    assert detect_format("# OpenCode\n\nSome rules.") == "opencode"


def test_detect_format_windsurf() -> None:
    assert detect_format("# Windsurf Rules\n\nFoo.") == "windsurf"


def test_detect_format_skill() -> None:
    assert detect_format("# Skill Name\n\nThis is a skill workflow for doing things.") == "skill"


def test_detect_format_agents() -> None:
    assert detect_format("# AGENTS\n\n## Instructions") == "agents"


def test_detect_format_agents_by_phrase() -> None:
    assert detect_format("Agent Instructions follow here.") == "agents"


def test_detect_format_unknown() -> None:
    assert detect_format("Just some random text with no clue.") is None


# ── convert: unsupported pair raises ─────────────────────────────────────────────

def test_convert_unsupported_raises() -> None:
    with pytest.raises(ValueError, match="not supported"):
        convert("# Some content", "claude", "cursor")


# ── convert: claude → agents heading rules ───────────────────────────────────────

_CLAUDE_SAMPLE = """\
# Project Instructions

## Overview

Short overview.

## Behavior

- Follow conventions.

## Rules

- No commits.

## Required Commands

```bash
uv run pytest
```
"""

def test_convert_claude_to_agents_headings() -> None:
    result = convert(_CLAUDE_SAMPLE, "claude", "agents")
    assert "# Agent Instructions" in result
    assert "## Instructions" in result
    assert "## Constraints" in result
    assert "## Verification" in result
    assert "# Project Instructions" not in result


def test_convert_claude_to_agents_term_replacement() -> None:
    text = "This is for Claude Code and CLAUDE.md settings."
    result = convert(text, "claude", "agents")
    assert "the agent" in result
    assert "AGENTS.md" in result
    assert "Claude Code" not in result
    assert "CLAUDE.md" not in result


# ── convert: agents → claude ─────────────────────────────────────────────────────

_AGENTS_SAMPLE = """\
# Agent Instructions

## Purpose

Purpose section.

## Instructions

- Do stuff.

## Constraints

- No commits.

## Verification

```bash
uv run pytest
```
"""

def test_convert_agents_to_claude_headings() -> None:
    result = convert(_AGENTS_SAMPLE, "agents", "claude")
    assert "# Project Instructions" in result
    assert "## Behavior" in result
    assert "## Rules" in result
    assert "## Required Commands" in result
    assert "# Agent Instructions" not in result


def test_convert_agents_to_claude_term_replacement() -> None:
    text = "See AGENTS.md for details."
    result = convert(text, "agents", "claude")
    assert "CLAUDE.md" in result
    assert "AGENTS.md" not in result


# ── convert: code blocks are preserved ───────────────────────────────────────────

def test_convert_code_block_not_transformed() -> None:
    text = "# Project Instructions\n\n```bash\nClaude Code is here\nCLAUDE.md rules\n```\n"
    result = convert(text, "claude", "agents")
    # Headings outside the block are transformed
    assert "# Agent Instructions" in result
    # Content inside the block should be untouched
    assert "Claude Code is here" in result
    assert "CLAUDE.md rules" in result


def test_convert_multiple_code_blocks_preserved() -> None:
    text = "# Project Instructions\n\n```bash\nClaude runs here\n```\n\nand ```inline``` too"
    result = convert(text, "claude", "agents")
    assert "Claude runs here" in result


# ── convert: cursor → agents ─────────────────────────────────────────────────────

def test_convert_cursor_to_agents() -> None:
    text = "# Cursor Rules\n\n## Project Context\n\nContext.\n\n## Coding Standards\n\nStandards."
    result = convert(text, "cursor", "agents")
    assert "# Agent Instructions" in result
    assert "## Purpose" in result
    assert "## Instructions" in result


def test_convert_cursor_term_replacement() -> None:
    text = "Use CURSOR.md and Cursor for guidance."
    result = convert(text, "cursor", "agents")
    assert "AGENTS.md" in result
    assert "the agent" in result


# ── convert: agents → cursor ─────────────────────────────────────────────────────

def test_convert_agents_to_cursor() -> None:
    text = "# Agent Instructions\n\n## Purpose\n\nFoo.\n\n## Instructions\n\nBar."
    result = convert(text, "agents", "cursor")
    assert "# Cursor Rules" in result
    assert "## Project Context" in result
    assert "## Coding Standards" in result


# ── convert: windsurf → agents ───────────────────────────────────────────────────

def test_convert_windsurf_to_agents() -> None:
    text = "# Windsurf Rules\n\n## Standards\n\nDo things."
    result = convert(text, "windsurf", "agents")
    assert "# Agent Instructions" in result
    assert "## Instructions" in result


def test_convert_windsurf_term_replacement() -> None:
    text = "Use .windsurfrules for Windsurf guidance."
    result = convert(text, "windsurf", "agents")
    assert "AGENTS.md" in result


# ── convert: skill → agents ───────────────────────────────────────────────────────

def test_convert_skill_to_agents() -> None:
    text = "# Skill Deploy\n\n## Steps\n\n1. Do step.\n\n## Inputs\n\n- source\n\n## Outputs\n\n- result"
    result = convert(text, "skill", "agents")
    assert "# Agent Instructions:" in result
    assert "## Instructions" in result
    assert "## Requirements" in result
    assert "## Expected Output" in result


# ── convert: gemini ───────────────────────────────────────────────────────────────

def test_convert_gemini_to_agents() -> None:
    text = "# Gemini Instructions\n\n## Project Context\n\nFoo.\n\n## Coding Standards\n\nBar."
    result = convert(text, "gemini", "agents")
    assert "# Agent Instructions" in result
    assert "## Purpose" in result


def test_convert_agents_to_gemini() -> None:
    text = "# Agent Instructions\n\n## Purpose\n\nFoo.\n\n## Instructions\n\nBar."
    result = convert(text, "agents", "gemini")
    assert "# Gemini Instructions" in result
    assert "## Project Context" in result
    assert "## Coding Standards" in result


# ── convert: opencode ────────────────────────────────────────────────────────────

def test_convert_opencode_to_agents() -> None:
    text = "# OpenCode\n\n## Project Context\n\nFoo.\n\n## Coding Standards\n\nBar."
    result = convert(text, "opencode", "agents")
    assert "# Agent Instructions" in result


def test_convert_agents_to_opencode() -> None:
    text = "# Agent Instructions\n\n## Purpose\n\nFoo."
    result = convert(text, "agents", "opencode")
    assert "# OpenCode" in result


# ── convert: agents → windsurf ───────────────────────────────────────────────────

def test_convert_agents_to_windsurf() -> None:
    text = "# Agent Instructions\n\n## Purpose\n\nFoo.\n\n## Instructions\n\nBar."
    result = convert(text, "agents", "windsurf")
    assert "# Windsurf Rules" in result
    assert "## Project Context" in result
    assert "## Standards" in result


def test_convert_agents_to_windsurf_term_replacement() -> None:
    text = "See AGENTS.md for details."
    result = convert(text, "agents", "windsurf")
    assert ".windsurfrules" in result


# ── FORMATS list integrity ────────────────────────────────────────────────────────

def test_all_formats_have_required_keys() -> None:
    for fmt in FORMATS:
        assert "id" in fmt
        assert "label" in fmt
        assert "filename" in fmt
