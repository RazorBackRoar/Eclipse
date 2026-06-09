# src/eclipse/importer.py
"""Import scanner for existing workspace configurations."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .catalog import CATALOG


@dataclass
class ImportCandidate:
    """A file found in the workspace that matches a known template."""
    path: Path
    relative_path: str
    template_id: str
    category: str
    content: str


def scan_for_configs(folder: Path) -> list[ImportCandidate]:
    """Walk a folder and find files that match known template filenames.

    Returns a list of candidates that can be imported into the UserTemplateStore.
    """
    candidates: list[ImportCandidate] = []

    # Pre-compute a mapping of (filename, parent_folder_name) -> template_id
    # We use parent_folder_name to disambiguate 'rules.md' for cursor vs windsurf,
    # or 'AGENTS.md' in .codex vs .agents.

    matcher: dict[tuple[str, str], str] = {}
    fallback_matcher: dict[str, str] = {} # Just filename -> template_id

    for t in CATALOG:
        # What would the parent folder be if it was exported?
        # e.g., hidden_folder=".windsurf" means parent is ".windsurf"
        # If no hidden_folder, parent is "" (root)

        parent_dir = ""
        if t.hidden_folder:
            parent_dir = Path(t.hidden_folder).name
        elif t.normal_folder:
            parent_dir = Path(t.normal_folder).name

        matcher[(t.filename, parent_dir)] = t.id
        # Also store a fallback just by filename, taking the first one found
        if t.filename not in fallback_matcher:
            fallback_matcher[t.filename] = t.id

    # Walk the directory
    for dirpath, dirnames, filenames in os.walk(folder):
        current_dir = Path(dirpath)

        # Skip heavy/irrelevant directories
        if ".git" in dirnames:
            dirnames.remove(".git")
        if "node_modules" in dirnames:
            dirnames.remove("node_modules")
        if ".venv" in dirnames:
            dirnames.remove(".venv")
        if "venv" in dirnames:
            dirnames.remove("venv")
        if "__pycache__" in dirnames:
            dirnames.remove("__pycache__")

        parent_name = current_dir.name if current_dir != folder else ""

        for filename in filenames:
            # Check exact match with parent folder context
            template_id = matcher.get((filename, parent_name))

            # If not found, try fallback (e.g. AGENTS.md in root)
            if not template_id:
                template_id = fallback_matcher.get(filename)

            if template_id:
                full_path = current_dir / filename

                try:
                    content = full_path.read_text(encoding="utf-8")
                except OSError:
                    continue # Skip unreadable files

                # Find category
                category = ""
                for t in CATALOG:
                    if t.id == template_id:
                        category = t.category
                        break

                rel_path = full_path.relative_to(folder)

                candidates.append(ImportCandidate(
                    path=full_path,
                    relative_path=str(rel_path),
                    template_id=template_id,
                    category=category,
                    content=content,
                ))

    return candidates
