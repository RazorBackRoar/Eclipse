# src/agentbox/exporters/claude_code.py
from __future__ import annotations

from pathlib import Path

from ..models import LibraryItem
from .base import BaseExporter


class ClaudeCodeExporter(BaseExporter):
    """Exporter for Claude Code."""

    target_name = "claude-code"

    def export_item(self, item: LibraryItem, out_dir: Path) -> list[Path]:
        written: list[Path] = []

        if item.type == "doc":
            render_as = self._render_as_for_target(item, "claude-code")

            if render_as == "CLAUDE.md":
                content = self.renderer.render("CLAUDE.md.j2", item)
                written.append(self.write_text(out_dir / "CLAUDE.md", content))

            if render_as == "AGENTS.md" or self._has_render(item, "claude-code", "AGENTS.md"):
                content = self.renderer.render("AGENTS.md.j2", item)
                written.append(self.write_text(out_dir / "AGENTS.md", content))

            readme_content = self.renderer.render("README.md.j2", item)
            written.append(self.write_text(out_dir / "README.md", readme_content))

        elif item.type == "agent":
            content = self.renderer.render("claude_agent.md.j2", item)
            agent_path = out_dir / ".claude" / "agents" / f"{item.id}.md"
            written.append(self.write_text(agent_path, content))

        elif item.type == "mcp_server":
            content = self.renderer.render("mcp_server.json.j2", item)
            mcp_path = out_dir / ".claude" / "mcp" / f"{item.id}.json"
            written.append(self.write_text(mcp_path, content))

        elif item.type == "skill":
            if item.root_dir is not None:
                entry_file = item.data.get("entry_file", "SKILL.md")
                src = item.root_dir / entry_file
                if src.exists():
                    skill_out = out_dir / ".claude" / "skills" / item.id / entry_file
                    skill_out.parent.mkdir(parents=True, exist_ok=True)
                    import shutil
                    shutil.copy2(src, skill_out)
                    written.append(skill_out)

        return written

    @staticmethod
    def _render_as_for_target(item: LibraryItem, target: str) -> str | None:
        for render in item.renders:
            if render.target == target:
                return render.render_as
        return None

    @staticmethod
    def _has_render(item: LibraryItem, target: str, render_as: str) -> bool:
        return any(
            r.target == target and r.render_as == render_as
            for r in item.renders
        )
