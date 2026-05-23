# src/agentbox/exporters/opencode.py
from __future__ import annotations

from pathlib import Path

from ..models import LibraryItem
from .base import BaseExporter


class OpenCodeExporter(BaseExporter):
    """Provisional exporter for OpenCode."""

    target_name = "opencode"

    # These paths are provisional — override via config once verified
    AGENTS_DIR = "agents"
    MCP_DIR = "mcp"
    CONFIG_DIR = "config"

    def export_item(self, item: LibraryItem, out_dir: Path) -> list[Path]:
        written: list[Path] = []

        if item.type == "doc":
            agents_content = self.renderer.render("AGENTS.md.j2", item)
            written.append(self.write_text(out_dir / "AGENTS.md", agents_content))

            readme_content = self.renderer.render("README.md.j2", item)
            written.append(self.write_text(out_dir / "README.md", readme_content))

        elif item.type == "agent":
            agents_content = self.renderer.render("AGENTS.md.j2", item)
            written.append(self.write_text(out_dir / "AGENTS.md", agents_content))

            # Use codex_agent template as a reasonable default until OpenCode
            # format is verified
            agent_content = self.renderer.render("codex_agent.md.j2", item)
            agent_path = out_dir / self.AGENTS_DIR / f"{item.id}.md"
            written.append(self.write_text(agent_path, agent_content))

        elif item.type == "mcp_server":
            content = self.renderer.render("mcp_server.json.j2", item)
            mcp_path = out_dir / self.MCP_DIR / f"{item.id}.json"
            written.append(self.write_text(mcp_path, content))

        return written
