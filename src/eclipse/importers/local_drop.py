# src/agentbox/importers/local_drop.py
from __future__ import annotations

from pathlib import Path

from .base import ImportResult
from .scanner import scan_path


def handle_local_drop(path: str | Path) -> ImportResult:
    """Entry point for local file or folder drag-and-drop import."""
    p = Path(path).resolve()

    if not p.exists():
        res = ImportResult(source_label=str(path), working_dir=p)
        res.warnings.append(f"Dropped path does not exist: {path}")
        return res

    return scan_path(p)
