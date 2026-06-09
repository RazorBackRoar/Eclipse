# src/eclipse/safe_export.py
"""Safe export engine for Eclipse.

Computes export plans, checks for conflicts, supports normal/hidden folder
output, and never overwrites without explicit approval.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExportItem:
    """A single file to be written during export."""

    relative_path: str
    content: str
    conflict: bool = False
    existing_content: str = ""

    def diff_lines(self) -> list[str]:
        """Return a unified diff between the existing content and new content."""
        if not self.conflict or not self.existing_content:
            return []

        import difflib

        old_lines = self.existing_content.splitlines()
        new_lines = self.content.splitlines()

        diff = list(difflib.unified_diff(
            old_lines, new_lines,
            fromfile=f"a/{self.relative_path}",
            tofile=f"b/{self.relative_path}",
            lineterm=""
        ))
        return diff


@dataclass
class ExportPlan:
    """A plan describing what an export will write to disk."""

    destination: Path
    items: list[ExportItem] = field(default_factory=list)
    use_hidden: bool = False

    @property
    def has_conflicts(self) -> bool:
        return any(item.conflict for item in self.items)

    @property
    def conflict_paths(self) -> list[str]:
        return [item.relative_path for item in self.items if item.conflict]

    def summary_lines(self) -> list[str]:
        """Human-readable summary of the export plan."""
        lines: list[str] = []
        mode = "hidden" if self.use_hidden else "normal"
        lines.append(f"Destination: {self.destination}")
        lines.append(f"Mode: {mode}")
        lines.append(f"Files: {len(self.items)}")
        if self.has_conflicts:
            lines.append(f"Conflicts: {len(self.conflict_paths)}")
        lines.append("")
        for item in self.items:
            marker = " ⚠ EXISTS" if item.conflict else ""
            lines.append(f"  {item.relative_path}{marker}")

            if item.conflict:
                diff = item.diff_lines()
                if diff:
                    lines.append("    --- Diff ---")
                    for dline in diff[:10]: # show first 10 lines of diff
                        lines.append(f"    {dline}")
                    if len(diff) > 10:
                        lines.append(f"    ... ({len(diff) - 10} more lines)")
                    lines.append("    ------------")
        return lines


def build_export_plan(
    destination: Path,
    files: list[tuple[str, str]],
    use_hidden: bool = False,
) -> ExportPlan:
    """Build an export plan without writing anything to disk.

    Args:
        destination: The root output directory.
        files: List of (relative_path, content) tuples.
        use_hidden: If True, prefix folder names with a dot.

    Returns:
        An ExportPlan describing what would be written.
    """
    plan = ExportPlan(destination=destination, use_hidden=use_hidden)

    for relative_path, content in files:
        if use_hidden:
            relative_path = _apply_hidden(relative_path)

        full_path = destination / relative_path
        conflict = full_path.exists()
        existing_content = ""
        if conflict:
            try:
                existing_content = full_path.read_text(encoding="utf-8")
            except OSError:
                pass

        plan.items.append(ExportItem(
            relative_path=relative_path,
            content=content,
            conflict=conflict,
            existing_content=existing_content,
        ))

    return plan


def execute_export(plan: ExportPlan, overwrite: bool = False) -> list[Path]:
    """Execute an export plan, writing files to disk.

    Args:
        plan: The export plan to execute.
        overwrite: If True, overwrite existing files. If False, skip conflicts.

    Returns:
        List of paths that were actually written.
    """
    written: list[Path] = []

    for item in plan.items:
        if item.conflict and not overwrite:
            continue

        full_path = plan.destination / item.relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        content = item.content
        if not content.endswith("\n"):
            content += "\n"

        full_path.write_text(content, encoding="utf-8")
        written.append(full_path)

    return written


def _apply_hidden(relative_path: str) -> str:
    """Convert a relative path to its hidden-folder equivalent.

    Only applies the dot prefix to the first path component if it's a folder name.
    Standalone filenames (like AGENTS.md) are not hidden.
    """
    parts = relative_path.split("/", 1)

    if len(parts) == 1:
        # Standalone file — don't hide it
        return relative_path

    folder = parts[0]
    rest = parts[1]

    if not folder.startswith("."):
        folder = "." + folder

    return f"{folder}/{rest}"
