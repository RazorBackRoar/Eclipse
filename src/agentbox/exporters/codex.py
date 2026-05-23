# src/agentbox/exporters/codex.py
from __future__ import annotations

import shutil
from pathlib import Path

from ..models import LibraryItem
from .base import BaseExporter


class CodexExporter(BaseExporter):
    """Exporter for OpenAI Codex."""

    target_name = "codex"

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

            agent_content = self.renderer.render("codex_agent.md.j2", item)
            agent_path = out_dir / ".codex" / "agents" / f"{item.id}.md"
            written.append(self.write_text(agent_path, agent_content))

        elif item.type == "skill":
            if item.root_dir is not None:
                entry_file = item.data.get("entry_file", "SKILL.md")
                src = item.root_dir / entry_file
                if src.exists():
                    skill_out = out_dir / ".codex" / "skills" / item.id / entry_file
                    skill_out.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, skill_out)
                    written.append(skill_out)

                    # Copy any listed resource files
                    for resource in item.data.get("resources", []):
                        res_src = item.root_dir / resource
                        if res_src.exists():
                            res_dst = out_dir / ".codex" / "skills" / item.id / resource
                            res_dst.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(res_src, res_dst)
                            written.append(res_dst)

        elif item.type == "mcp_server":
            content = self.renderer.render("mcp_server.json.j2", item)
            mcp_path = out_dir / ".codex" / "mcp" / f"{item.id}.json"
            written.append(self.write_text(mcp_path, content))

        return written
