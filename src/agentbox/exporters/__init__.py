# src/agentbox/exporters/__init__.py
from .claude_code import ClaudeCodeExporter
from .codex import CodexExporter
from .cursor import CursorExporter
from .opencode import OpenCodeExporter
from .windsurf import WindsurfExporter


# Central registry: target name → exporter class
EXPORTER_CLASSES: dict[str, type] = {
    "claude-code": ClaudeCodeExporter,
    "codex":       CodexExporter,
    "cursor":      CursorExporter,
    "windsurf":    WindsurfExporter,
    "opencode":    OpenCodeExporter,
}

__all__ = [
    "ClaudeCodeExporter",
    "CodexExporter",
    "CursorExporter",
    "WindsurfExporter",
    "OpenCodeExporter",
    "EXPORTER_CLASSES",
]
