from pathlib import Path

from agentbox import paths


def test_project_roots_are_consistent() -> None:
    project = paths.project_root()

    assert paths.library_root() == project / "library"
    assert paths.exports_root() == project / "exports"
    assert paths.backups_root() == project / "backups"
    assert paths.workspace_settings_path() == project / "library" / "workspace_settings.json"


def test_workspace_settings_roundtrip(tmp_path: Path, monkeypatch) -> None:
    settings_path = tmp_path / "workspace_settings.json"
    monkeypatch.setattr(paths, "workspace_settings_path", lambda: settings_path)

    workspace = tmp_path / "workspace"
    workspace.mkdir()

    paths.set_workspace(workspace)
    resolved = paths.get_workspace()

    assert resolved == workspace
