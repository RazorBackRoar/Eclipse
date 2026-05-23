# src/agentbox/skill_preview.py
from __future__ import annotations

from pathlib import Path

from .models import LibraryItem


MAX_PREVIEW_LINES = 44
MAX_PREVIEW_CHARS = 6000


def skill_markdown_preview(item: LibraryItem) -> str | None:
    if item.type != "skill" or item.root_dir is None:
        return None

    entry_file = item.data.get("entry_file", "SKILL.md")
    entry_path = item.root_dir / entry_file
    if not entry_path.exists() or not entry_path.is_file():
        return None

    return _read_top(entry_path)


def _read_top(path: Path) -> str:
    lines: list[str] = []
    char_count = 0

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if len(lines) >= MAX_PREVIEW_LINES or char_count >= MAX_PREVIEW_CHARS:
                lines.append("\n[Preview truncated]")
                break

            lines.append(line.rstrip("\n"))
            char_count += len(line)

    return "\n".join(lines)
