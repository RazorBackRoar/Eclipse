# src/agentbox/export_formats.py
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from .models import LibraryItem
from .render import TemplateRenderer


@dataclass(frozen=True)
class ExportFormat:
    id: str
    label: str


EXPORT_FORMATS: tuple[ExportFormat, ...] = (
    ExportFormat("agent_file", ".agent"),
    ExportFormat("claude_file", ".claude"),
    ExportFormat("skills_folder", ".skills"),
    ExportFormat("agents_md", "AGENTS.md"),
    ExportFormat("claude_md", "CLAUDE.md"),
    ExportFormat("mcp_bundle", "MCP bundle"),
    ExportFormat("mcp_file", "MCP file"),
    ExportFormat("original_folder", "Original folder"),
    ExportFormat("readme", "README"),
    ExportFormat("skill_md", "SKILL.md"),
    ExportFormat("target_export", "Target app export"),
)


def export_item_as_format(
    item: LibraryItem,
    renderer: TemplateRenderer,
    out_dir: Path,
    export_format: str,
) -> list[Path]:
    if export_format == "agent_file":
        return [_write_rendered(renderer, item, out_dir / f"{item.id}.agent", "codex_agent.md.j2")]

    if export_format == "claude_file":
        return [_write_rendered(renderer, item, out_dir / f"{item.id}.claude", "CLAUDE.md.j2")]

    if export_format == "skills_folder":
        return _export_skills_folder(item, out_dir)

    if export_format == "agents_md":
        return [_write_rendered(renderer, item, out_dir / "AGENTS.md", "AGENTS.md.j2")]

    if export_format == "claude_md":
        return [_write_rendered(renderer, item, out_dir / "CLAUDE.md", "CLAUDE.md.j2")]

    if export_format == "mcp_bundle":
        return _copy_item_folder(item, out_dir / "mcp" / item.id)

    if export_format == "mcp_file":
        return _export_mcp_file(item, out_dir)

    if export_format == "original_folder":
        return _copy_item_folder(item, out_dir / item.id)

    if export_format == "readme":
        return [_write_rendered(renderer, item, out_dir / "README.md", "README.md.j2")]

    if export_format == "skill_md":
        return _export_skill_entry(item, out_dir)

    raise ValueError(f"Unknown export format: {export_format}")


def export_format_label(export_format: str) -> str:
    for option in EXPORT_FORMATS:
        if option.id == export_format:
            return option.label
    return export_format


def _write_rendered(
    renderer: TemplateRenderer,
    item: LibraryItem,
    path: Path,
    template_name: str,
) -> Path:
    content = renderer.render(template_name, item)
    return _write_text(path, content)


def _write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    return path


def _copy_item_folder(item: LibraryItem, destination: Path) -> list[Path]:
    if item.root_dir is None:
        raise ValueError(f"{item.name} has no folder to export.")

    if destination.exists():
        shutil.rmtree(destination)

    shutil.copytree(item.root_dir, destination)
    return _sorted_files(destination)


def _export_skills_folder(item: LibraryItem, out_dir: Path) -> list[Path]:
    if item.type != "skill":
        raise ValueError(".skills export is only available for skill items.")

    return _copy_item_folder(item, out_dir / ".skills" / item.id)


def _export_skill_entry(item: LibraryItem, out_dir: Path) -> list[Path]:
    if item.type != "skill":
        raise ValueError("SKILL.md export is only available for skill items.")

    src = _item_sidecar(item, item.data.get("entry_file", "SKILL.md"))
    if src is None:
        raise ValueError(f"{item.name} does not have a SKILL.md file.")

    dst = out_dir / "SKILL.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return [dst]


def _export_mcp_file(item: LibraryItem, out_dir: Path) -> list[Path]:
    if item.type != "mcp_server":
        raise ValueError("MCP file export is only available for MCP items.")

    source_file = item.data.get("source_file", "server.json")
    src = _item_sidecar(item, source_file)
    if src is None:
        raise ValueError(f"{item.name} does not have an MCP source file.")

    dst = out_dir / src.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return [dst]


def _item_sidecar(item: LibraryItem, relative_path: str) -> Path | None:
    if item.root_dir is None:
        return None

    path = item.root_dir / relative_path
    if not path.exists() or not path.is_file():
        return None

    return path


def _sorted_files(root: Path) -> list[Path]:
    return sorted((path for path in root.rglob("*") if path.is_file()), key=lambda path: str(path).lower())
