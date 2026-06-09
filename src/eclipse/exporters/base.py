# src/eclipse/exporters/base.py
from __future__ import annotations

from pathlib import Path

from ..models import LibraryItem
from ..render import TemplateRenderer


class BaseExporter:
    """Abstract base class for all Eclipse exporters."""

    target_name: str = "base"

    def __init__(self, renderer: TemplateRenderer) -> None:
        self.renderer = renderer

    def export_item(self, item: LibraryItem, out_dir: Path) -> list[Path]:
        """Export a library item into the target-specific file layout."""
        raise NotImplementedError(
            f"{self.__class__.__name__}.export_item() is not implemented"
        )

    @staticmethod
    def write_text(path: Path, content: str) -> Path:
        """Write text to a file, creating parent directories as needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        if not content.endswith("\n"):
            content += "\n"
        path.write_text(content, encoding="utf-8")
        return path

    def _read_sidecar(self, item: LibraryItem, relative_path: str) -> str:
        """Read a sidecar file from the item's root directory."""
        if item.root_dir is None:
            return ""
        full_path = item.root_dir / relative_path
        if not full_path.exists():
            return ""
        return full_path.read_text(encoding="utf-8")
