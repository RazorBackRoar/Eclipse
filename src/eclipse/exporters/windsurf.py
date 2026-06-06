# src/agentbox/exporters/windsurf.py
from __future__ import annotations

from pathlib import Path

from ..models import LibraryItem
from .base import BaseExporter


class WindsurfExporter(BaseExporter):
    """Exporter for Windsurf."""

    target_name = "windsurf"

    def export_item(self, item: LibraryItem, out_dir: Path) -> list[Path]:
        written: list[Path] = []

        if item.type in ("doc", "agent"):
            content = self.renderer.render("AGENTS.md.j2", item)
            written.append(self.write_text(out_dir / "AGENTS.md", content))

        if item.type == "rule":
            content = self.renderer.render("AGENTS.md.j2", item)  # rule text as md
            rule_path = out_dir / ".windsurf" / "rules" / f"{item.id}.md"
            written.append(self.write_text(rule_path, content))

        if item.type == "workflow":
            content = self.renderer.render("windsurf_workflow.md.j2", item)
            workflow_path = out_dir / ".windsurf" / "workflows" / f"{item.id}.md"
            written.append(self.write_text(workflow_path, content))

        if item.type == "mcp_server":
            content = self.renderer.render("mcp_server.json.j2", item)
            mcp_path = out_dir / ".windsurf" / "mcp" / f"{item.id}.json"
            written.append(self.write_text(mcp_path, content))

        return written
