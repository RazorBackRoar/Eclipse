# src/eclipse/importers/github_url.py
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from .base import ImportResult
from .scanner import scan_path


def handle_github_import(url: str) -> ImportResult:
    """Clones a GitHub repository into a temporary directory and scans it."""
    url = url.strip()
    if not url.endswith(".git") and "github.com" in url:
        # Basic normalization: add .git if missing from github.com URLs
        parts = url.split("?")[0].rstrip("/")
        if not parts.endswith(".git"):
            url = parts + ".git"

    temp_dir = tempfile.mkdtemp(prefix="eclipse-clone-")
    temp_path = Path(temp_dir)

    result = ImportResult(source_label=url, working_dir=temp_path)

    try:
        # ── Clone from GitHub ────────────────────────────────────────────────────
        process = subprocess.run(
            ["git", "clone", "--depth", "1", url, str(temp_path)],
            capture_output=True,
            text=True,
            check=False,
        )

        if process.returncode != 0:
            result.warnings.append(f"Git clone failed: {process.stderr.strip()}")
            return result

        # ── Scan the clone ───────────────────────────────────────────────────────
        scan_res = scan_path(temp_path)
        result.detected_items = scan_res.detected_items
        result.warnings.extend(scan_res.warnings)

    except Exception as exc:
        result.warnings.append(f"Internal error during GitHub import: {exc}")

    return result
