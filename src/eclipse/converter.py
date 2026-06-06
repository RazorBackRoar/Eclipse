# src/agentbox/converter.py
"""Rule-based text converter between workspace config formats.

Converts between CLAUDE.md, CURSOR.md, GEMINI.md, and AGENTS.md
using regex-based heading/term replacement. Never invents new content.
"""
from __future__ import annotations

import re


# ── Format definitions ────────────────────────────────────────────────────────────

FORMATS: list[dict[str, str]] = [
    {"id": "agents", "label": "AGENTS.md", "filename": "AGENTS.md"},
    {"id": "claude", "label": "CLAUDE.md", "filename": "CLAUDE.md"},
    {"id": "cursor", "label": "CURSOR.md", "filename": "CURSOR.md"},
    {"id": "gemini", "label": "GEMINI.md", "filename": "GEMINI.md"},
    {"id": "opencode", "label": "OPENCODE.md", "filename": "OPENCODE.md"},
    {"id": "windsurf", "label": ".windsurfrules", "filename": ".windsurfrules"},
    {"id": "skill", "label": "SKILL.md", "filename": "SKILL.md"},
]

FORMAT_IDS: list[str] = [f["id"] for f in FORMATS]


def format_label(fmt_id: str) -> str:
    for f in FORMATS:
        if f["id"] == fmt_id:
            return f["label"]
    return fmt_id


# ── Conversion pairs ─────────────────────────────────────────────────────────────

VALID_CONVERSIONS: list[tuple[str, str]] = [
    ("claude", "agents"),
    ("cursor", "agents"),
    ("gemini", "agents"),
    ("opencode", "agents"),
    ("windsurf", "agents"),
    ("agents", "claude"),
    ("agents", "cursor"),
    ("agents", "gemini"),
    ("agents", "opencode"),
    ("agents", "windsurf"),
    ("skill", "agents"),
]


def can_convert(source: str, target: str) -> bool:
    return (source, target) in VALID_CONVERSIONS


def available_targets(source: str) -> list[str]:
    return [t for s, t in VALID_CONVERSIONS if s == source]


# ── Detection ─────────────────────────────────────────────────────────────────────

def detect_format(text: str) -> str | None:
    """Attempt to detect the source format from text content."""
    first_lines = text[:500].lower()

    if "project instructions" in first_lines or "claude" in first_lines:
        return "claude"
    if "cursor" in first_lines:
        return "cursor"
    if "gemini" in first_lines:
        return "gemini"
    if "opencode" in first_lines:
        return "opencode"
    if "windsurf" in first_lines:
        return "windsurf"
    if "skill" in first_lines and "workflow" in first_lines:
        return "skill"
    if "agents" in first_lines or "agent instructions" in first_lines:
        return "agents"
    return None


# ── Core converter ────────────────────────────────────────────────────────────────

def convert(text: str, source: str, target: str) -> str:
    """Convert text from source format to target format.

    Preserves code blocks, paths, command blocks, warnings, and safety rules.
    Never invents new content — only transforms headings and tool-specific terms.
    """
    if not can_convert(source, target):
        raise ValueError(f"Conversion from {source} to {target} is not supported.")

    # Protect code blocks from transformation
    blocks: list[str] = []
    protected = _protect_code_blocks(text, blocks)

    # Apply transformation rules
    result = _apply_rules(protected, source, target)

    # Restore code blocks
    result = _restore_code_blocks(result, blocks)

    return result


# ── Internal helpers ──────────────────────────────────────────────────────────────

_CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
_PLACEHOLDER = "\x00CODEBLOCK_{}\x00"


def _protect_code_blocks(text: str, blocks: list[str]) -> str:
    """Replace code blocks with placeholders to prevent transformation."""
    def replacer(match: re.Match[str]) -> str:
        idx = len(blocks)
        blocks.append(match.group(0))
        return _PLACEHOLDER.format(idx)
    return _CODE_BLOCK_RE.sub(replacer, text)


def _restore_code_blocks(text: str, blocks: list[str]) -> str:
    """Restore code blocks from placeholders."""
    for idx, block in enumerate(blocks):
        text = text.replace(_PLACEHOLDER.format(idx), block)
    return text


# ── Heading rules ─────────────────────────────────────────────────────────────────

_HEADING_RULES: dict[tuple[str, str], list[tuple[str, str]]] = {
    # Claude → Agents
    ("claude", "agents"): [
        (r"^#\s+Project Instructions", "# Agent Instructions"),
        (r"^##\s+Behavior\b", "## Instructions"),
        (r"^##\s+Rules\b", "## Constraints"),
        (r"^##\s+Required Commands\b", "## Verification"),
        (r"^##\s+Required Environment Variables\b", "## Environment"),
    ],
    # Agents → Claude
    ("agents", "claude"): [
        (r"^#\s+(?:Agent Instructions|AGENTS)\b", "# Project Instructions"),
        (r"^##\s+Instructions\b", "## Behavior"),
        (r"^##\s+Constraints\b", "## Rules"),
        (r"^##\s+Verification\b", "## Required Commands"),
        (r"^##\s+Environment\b", "## Required Environment Variables"),
    ],
    # Cursor → Agents
    ("cursor", "agents"): [
        (r"^#\s+Cursor Rules\b", "# Agent Instructions"),
        (r"^##\s+Project Context\b", "## Purpose"),
        (r"^##\s+Coding Standards\b", "## Instructions"),
    ],
    # Agents → Cursor
    ("agents", "cursor"): [
        (r"^#\s+(?:Agent Instructions|AGENTS)\b", "# Cursor Rules"),
        (r"^##\s+Purpose\b", "## Project Context"),
        (r"^##\s+Instructions\b", "## Coding Standards"),
    ],
    # Gemini → Agents
    ("gemini", "agents"): [
        (r"^#\s+Gemini Instructions\b", "# Agent Instructions"),
        (r"^##\s+Project Context\b", "## Purpose"),
        (r"^##\s+Coding Standards\b", "## Instructions"),
    ],
    # Agents → Gemini
    ("agents", "gemini"): [
        (r"^#\s+(?:Agent Instructions|AGENTS)\b", "# Gemini Instructions"),
        (r"^##\s+Purpose\b", "## Project Context"),
        (r"^##\s+Instructions\b", "## Coding Standards"),
    ],
    # OpenCode → Agents
    ("opencode", "agents"): [
        (r"^#\s+OpenCode(?: Rules)?\b", "# Agent Instructions"),
        (r"^##\s+Project Context\b", "## Purpose"),
        (r"^##\s+Coding Standards\b", "## Instructions"),
    ],
    # Agents → OpenCode
    ("agents", "opencode"): [
        (r"^#\s+(?:Agent Instructions|AGENTS)\b", "# OpenCode"),
        (r"^##\s+Purpose\b", "## Project Context"),
        (r"^##\s+Instructions\b", "## Coding Standards"),
    ],
    # Windsurf → Agents
    ("windsurf", "agents"): [
        (r"^#\s+Windsurf Rules\b", "# Agent Instructions"),
        (r"^##\s+Project Context\b", "## Purpose"),
        (r"^##\s+Standards\b", "## Instructions"),
    ],
    # Agents → Windsurf
    ("agents", "windsurf"): [
        (r"^#\s+(?:Agent Instructions|AGENTS)\b", "# Windsurf Rules"),
        (r"^##\s+Purpose\b", "## Project Context"),
        (r"^##\s+Instructions\b", "## Standards"),
    ],
    # Skill → Agents
    ("skill", "agents"): [
        (r"^#\s+Skill\s+", "# Agent Instructions: "),
        (r"^##\s+Steps\b", "## Instructions"),
        (r"^##\s+Inputs\b", "## Requirements"),
        (r"^##\s+Outputs\b", "## Expected Output"),
    ],
}

# ── Term replacement rules ────────────────────────────────────────────────────────

_TERM_RULES: dict[tuple[str, str], list[tuple[str, str]]] = {
    ("claude", "agents"): [
        ("CLAUDE.md", "AGENTS.md"),
        ("Claude Code", "the agent"),
        ("Claude code", "the agent"),
        ("claude code", "the agent"),
        ("Claude", "the agent"),
    ],
    ("agents", "claude"): [
        ("AGENTS.md", "CLAUDE.md"),
    ],
    ("cursor", "agents"): [
        ("CURSOR.md", "AGENTS.md"),
        ("Cursor", "the agent"),
        ("cursor", "the agent"),
    ],
    ("agents", "cursor"): [
        ("AGENTS.md", "CURSOR.md"),
    ],
    ("gemini", "agents"): [
        ("GEMINI.md", "AGENTS.md"),
        ("Gemini", "the agent"),
        ("gemini", "the agent"),
    ],
    ("agents", "gemini"): [
        ("AGENTS.md", "GEMINI.md"),
    ],
    ("opencode", "agents"): [
        ("OPENCODE.md", "AGENTS.md"),
        ("OpenCode", "the agent"),
        ("opencode", "the agent"),
    ],
    ("agents", "opencode"): [
        ("AGENTS.md", "OPENCODE.md"),
    ],
    ("windsurf", "agents"): [
        (".windsurfrules", "AGENTS.md"),
        ("Windsurf", "the agent"),
        ("windsurf", "the agent"),
    ],
    ("agents", "windsurf"): [
        ("AGENTS.md", ".windsurfrules"),
    ],
    ("skill", "agents"): [
        ("SKILL.md", "AGENTS.md"),
    ],
}


def _apply_rules(text: str, source: str, target: str) -> str:
    """Apply heading and term replacement rules."""
    key = (source, target)

    # Apply heading rules (line-by-line, regex on start of line)
    heading_rules = _HEADING_RULES.get(key, [])
    lines = text.split("\n")
    for i, line in enumerate(lines):
        for pattern, replacement in heading_rules:
            new_line = re.sub(pattern, replacement, line)
            if new_line != line:
                lines[i] = new_line
                break
    text = "\n".join(lines)

    # Apply term rules (whole-text, case-sensitive exact match)
    term_rules = _TERM_RULES.get(key, [])
    for old, new in term_rules:
        text = text.replace(old, new)

    return text
