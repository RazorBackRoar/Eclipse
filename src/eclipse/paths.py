# src/agentbox/paths.py
from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Returns the project root directory.

    This is computed by going 2 levels up from this file:
      src/agentbox/paths.py → src/agentbox/ → src/ → project root
    """
    return Path(__file__).resolve().parents[2]


def library_root() -> Path:
    """The canonical source-of-truth library directory."""
    return project_root() / "library"


def exports_root() -> Path:
    """The generated output directory. Treat as disposable."""
    return project_root() / "exports"


def templates_root() -> Path:
    """The Jinja2 templates directory inside the package."""
    return Path(__file__).resolve().parent / "templates"


def backups_root() -> Path:
    """Optional: directory for library snapshots."""
    return project_root() / "backups"


def target_export_dir(target: str) -> Path:
    """Returns the export directory for a specific tool target."""
    return exports_root() / target


def workspace_settings_path() -> Path:
    """Returns the path to the workspace settings JSON file."""
    return library_root() / "workspace_settings.json"


def get_workspace() -> Path | None:
    """Reads the active workspace path from settings."""
    import json
    settings_file = workspace_settings_path()
    if settings_file.exists():
        try:
            data = json.loads(settings_file.read_text(encoding="utf-8"))
            ws_path = data.get("active_workspace")
            if ws_path:
                return Path(ws_path)
        except (json.JSONDecodeError, OSError):
            pass
    return None


def set_workspace(path: Path) -> None:
    """Saves the active workspace path to settings."""
    import json
    settings_file = workspace_settings_path()
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if settings_file.exists():
        try:
            data = json.loads(settings_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    data["active_workspace"] = str(path)
    settings_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
