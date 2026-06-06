# src/agentbox/app.py
"""Eclipse application controller — manages template catalog, converter, and exports."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
)

from .catalog import ExportPresetStore, UserTemplateStore, template_by_id
from .paths import get_workspace, library_root, set_workspace
from .safe_export import build_export_plan, execute_export
from .ui.main_window import MainWindowWidget


class EclipseApp(QMainWindow):
    """Main application controller.

    Manages the template store, coordinates between the UI panels,
    and handles export operations.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Eclipse — Workspace Config Manager")
        self.resize(1100, 720)

        # ── Template store ──────────────────────────────────────────────────
        store_path = library_root() / "user_templates.json"
        store_path.parent.mkdir(parents=True, exist_ok=True)
        self.store = UserTemplateStore(store_path)

        # ── Export Preset Store ──────────────────────────────────────────────
        preset_path = library_root() / "export_presets.json"
        self.preset_store = ExportPresetStore(preset_path)

        # ── UI ──────────────────────────────────────────────────────────────
        self.view = MainWindowWidget(self)
        self.setCentralWidget(self.view)

        self._reload_workspace()

    # ── Public interface for panels ──────────────────────────────────────────

    def switch_workspace(self) -> None:
        """Prompt user to select a new active workspace."""
        current = get_workspace()
        start_dir = str(current) if current else ""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Active Workspace", start_dir
        )
        if folder:
            set_workspace(Path(folder))
            self._reload_workspace()
            self.set_status(f"Workspace set to: {folder}")

    def _reload_workspace(self) -> None:
        """Notify relevant UI components that the workspace changed."""
        self.view.export_panel._load_active_workspace()
        self.view.import_panel._load_active_workspace()

    def set_status(self, msg: str) -> None:
        """Update the status bar message."""
        self.view.set_status(msg)

    def export_template(
        self,
        template_id: str,
        content: str,
        use_hidden: bool,
    ) -> None:
        """Export a single template — triggered from the category panel."""
        entry = template_by_id(template_id)
        if not entry:
            self.set_status(f"Unknown template: {template_id}")
            return

        folder = QFileDialog.getExistingDirectory(
            self, "Choose export destination", ""
        )
        if not folder:
            return

        destination = Path(folder)

        # Build the relative path
        if entry.normal_folder:
            rel = f"{entry.normal_folder}/{entry.filename}"
        else:
            rel = entry.filename

        plan = build_export_plan(
            destination, [(rel, content)], use_hidden=use_hidden
        )

        # Show preview
        if plan.has_conflicts:
            conflicts = "\n".join(plan.conflict_paths)
            reply = QMessageBox.warning(
                self,
                "Existing Files",
                f"The following files already exist:\n\n{conflicts}\n\n"
                f"Overwrite them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                self.set_status("Export cancelled.")
                return
            overwrite = True
        else:
            overwrite = False

        written = execute_export(plan, overwrite=overwrite)
        if written:
            self.set_status(
                f"Exported: {written[0].relative_to(destination)}"
            )
        else:
            self.set_status("Nothing exported (skipped conflicts).")

    def update_preview(self) -> None:
        """Placeholder for backward compatibility. No-op in new UI."""
        pass
