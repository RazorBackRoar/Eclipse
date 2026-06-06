# src/agentbox/exporters/cursor.py
from __future__ import annotations

from pathlib import Path

from ..models import LibraryItem
from .base import BaseExporter


class CursorExporter(BaseExporter):
    """Exporter for Cursor."""

    target_name = "cursor"

    def export_item(self, item: LibraryItem, out_dir: Path) -> list[Path]:
        written: list[Path] = []

        if item.type in ("doc", "agent"):
            content = self.renderer.render("AGENTS.md.j2", item)
            written.append(self.write_text(out_dir / "AGENTS.md", content))

        if item.type == "rule":
            content = self.renderer.render("cursor_rule.mdc.j2", item)

            # Use output_path override if specified, otherwise default to <id>.mdc
            output_path = None
            for render in item.renders:
                if render.target == "cursor" and render.output_path:
                    output_path = render.output_path
                    break

            if output_path:
                rule_path = out_dir / output_path
            else:
                rule_path = out_dir / ".cursor" / "rules" / f"{item.id}.mdc"

            written.append(self.write_text(rule_path, content))

        return written
