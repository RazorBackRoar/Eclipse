# src/eclipse/ui/export_panel.py
"""Export tab UI — batch export with category/template selection and preview."""
from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..catalog import (
    CATEGORIES,
    template_by_id,
    templates_for_category,
)
from ..safe_export import ExportPlan, build_export_plan, execute_export


class ExportPanel(QWidget):
    """Export tab: select categories/templates, preview plan, execute export."""

    def __init__(self, app_controller: Any) -> None:
        super().__init__()
        self.app = app_controller
        self._current_plan: ExportPlan | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()
        title_layout = QVBoxLayout()
        title = QLabel("Export")
        title.setObjectName("section_title")

        helper = QLabel(
            "Select templates to export, choose a destination, "
            "and preview before writing."
        )
        helper.setObjectName("helper_text")
        helper.setWordWrap(True)
        title_layout.addWidget(title)
        title_layout.addWidget(helper)

        # Presets UI
        preset_layout = QHBoxLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(150)
        self.preset_combo.addItem("Select Preset...")

        self.load_preset_btn = QPushButton("Load")
        self.load_preset_btn.setObjectName("muted_action")
        self.load_preset_btn.clicked.connect(self._on_load_preset)

        self.save_preset_btn = QPushButton("Save as Preset")
        self.save_preset_btn.setObjectName("muted_action")
        self.save_preset_btn.clicked.connect(self._on_save_preset)

        preset_layout.addWidget(self.preset_combo)
        preset_layout.addWidget(self.load_preset_btn)
        preset_layout.addWidget(self.save_preset_btn)

        header_layout.addLayout(title_layout)
        header_layout.addStretch(1)
        header_layout.addLayout(preset_layout)

        layout.addLayout(header_layout)

        # Main content: two columns
        content_layout = QHBoxLayout()
        content_layout.setSpacing(14)

        # Left: template checklist
        left_frame = QFrame()
        left_frame.setObjectName("surface_panel")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(8)

        list_header = QHBoxLayout()
        list_label = QLabel("Templates")
        list_label.setObjectName("panel_label")
        self.select_all_btn = QPushButton("All")
        self.select_all_btn.setObjectName("muted_action")
        self.select_all_btn.setFixedWidth(50)
        self.select_all_btn.clicked.connect(self._select_all)
        self.select_none_btn = QPushButton("None")
        self.select_none_btn.setObjectName("muted_action")
        self.select_none_btn.setFixedWidth(50)
        self.select_none_btn.clicked.connect(self._select_none)
        list_header.addWidget(list_label)
        list_header.addStretch(1)
        list_header.addWidget(self.select_all_btn)
        list_header.addWidget(self.select_none_btn)

        self.template_list = QListWidget()
        self.template_list.setObjectName("export_list")

        left_layout.addLayout(list_header)
        left_layout.addWidget(self.template_list)

        content_layout.addWidget(left_frame, 1)

        # Right: preview
        right_frame = QFrame()
        right_frame.setObjectName("surface_panel")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(8)

        preview_label = QLabel("Export preview")
        preview_label.setObjectName("panel_label")
        self.preview_area = QTextEdit()
        self.preview_area.setObjectName("code_view")
        self.preview_area.setReadOnly(True)
        self.preview_area.setPlaceholderText(
            "Click 'Preview' to see what files will be created."
        )

        right_layout.addWidget(preview_label)
        right_layout.addWidget(self.preview_area)

        content_layout.addWidget(right_frame, 1)
        layout.addLayout(content_layout, 1)

        # Bottom controls
        bottom = QFrame()
        bottom.setObjectName("action_bar")
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(14, 10, 14, 10)
        bottom_layout.setSpacing(12)

        self.dest_label = QLabel("No destination selected")
        self.dest_label.setObjectName("helper_text")

        self.choose_dest_btn = QPushButton("Choose folder…")
        self.choose_dest_btn.setObjectName("muted_action")
        self.choose_dest_btn.clicked.connect(self._choose_destination)

        self.hidden_toggle = QPushButton("Hidden")
        self.hidden_toggle.setObjectName("toggle_btn")
        self.hidden_toggle.setCheckable(True)
        self.hidden_toggle.setToolTip("Export folders with a leading dot")

        self.preview_btn = QPushButton("Preview")
        self.preview_btn.setObjectName("muted_action")
        self.preview_btn.clicked.connect(self._on_preview)

        self.export_btn = QPushButton("Export")
        self.export_btn.setObjectName("primary_action")
        self.export_btn.clicked.connect(self._on_export)

        bottom_layout.addWidget(self.dest_label, 1)
        bottom_layout.addWidget(self.choose_dest_btn)
        bottom_layout.addWidget(self.hidden_toggle)
        bottom_layout.addWidget(self.preview_btn)
        bottom_layout.addWidget(self.export_btn)

        layout.addWidget(bottom)

        self._destination: str = ""
        self._populate_list()
        self.refresh_presets()

        # Load active workspace if set
        self._load_active_workspace()

    def _load_active_workspace(self) -> None:
        from ..paths import get_workspace
        ws = get_workspace()
        if ws and ws.exists():
            self._set_destination(str(ws))

    def refresh_presets(self) -> None:
        self.preset_combo.clear()
        self.preset_combo.addItem("Select Preset...")
        for name in self.app.preset_store.get_preset_names():
            self.preset_combo.addItem(name)

    def _on_save_preset(self) -> None:
        if not self._destination:
            self.app.set_status("Choose a destination before saving a preset.")
            return

        tids = self._checked_template_ids()
        if not tids:
            self.app.set_status("Select at least one template before saving a preset.")
            return

        name, ok = QInputDialog.getText(
            self, "Save Preset", "Preset name:"
        )
        if ok and name:
            self.app.preset_store.save_preset(
                name=name,
                template_ids=tids,
                destination=self._destination,
                use_hidden=self.hidden_toggle.isChecked()
            )
            self.refresh_presets()
            idx = self.preset_combo.findText(name)
            if idx >= 0:
                self.preset_combo.setCurrentIndex(idx)
            self.app.set_status(f"Saved preset: {name}")

    def _on_load_preset(self) -> None:
        name = self.preset_combo.currentText()
        if name == "Select Preset...":
            return

        preset = self.app.preset_store.get_preset(name)
        if not preset:
            return

        self._set_destination(preset.destination)
        self.hidden_toggle.setChecked(preset.use_hidden)

        for i in range(self.template_list.count()):
            item = self.template_list.item(i)
            if item and item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                tid = item.data(Qt.ItemDataRole.UserRole)
                if tid in preset.template_ids:
                    item.setCheckState(Qt.CheckState.Checked)
                else:
                    item.setCheckState(Qt.CheckState.Unchecked)

        self.app.set_status(f"Loaded preset: {name}")

    def _populate_list(self) -> None:
        self.template_list.clear()
        # Non-utility categories only
        exportable = [
            c for c in CATEGORIES if c["group"] != "utilities"
        ]

        for cat in exportable:
            # Category header (non-checkable)
            header_item = QListWidgetItem(f"── {cat['label']} ──")
            header_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.template_list.addItem(header_item)

            entries = templates_for_category(cat["id"])
            for entry in entries:
                item = QListWidgetItem(f"  {entry.display_name}")
                item.setFlags(
                    Qt.ItemFlag.ItemIsEnabled
                    | Qt.ItemFlag.ItemIsUserCheckable
                    | Qt.ItemFlag.ItemIsSelectable
                )
                item.setCheckState(Qt.CheckState.Unchecked)
                item.setData(Qt.ItemDataRole.UserRole, entry.id)
                self.template_list.addItem(item)

    def _select_all(self) -> None:
        for i in range(self.template_list.count()):
            item = self.template_list.item(i)
            if item and item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                item.setCheckState(Qt.CheckState.Checked)

    def _select_none(self) -> None:
        for i in range(self.template_list.count()):
            item = self.template_list.item(i)
            if item and item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                item.setCheckState(Qt.CheckState.Unchecked)

    def _checked_template_ids(self) -> list[str]:
        ids: list[str] = []
        for i in range(self.template_list.count()):
            item = self.template_list.item(i)
            if (
                item
                and item.flags() & Qt.ItemFlag.ItemIsUserCheckable
                and item.checkState() == Qt.CheckState.Checked
            ):
                tid = item.data(Qt.ItemDataRole.UserRole)
                if tid:
                    ids.append(tid)
        return ids

    def _set_destination(self, folder: str) -> None:
        self._destination = folder
        display = folder if len(folder) < 60 else "…" + folder[-55:]
        self.dest_label.setText(f"Destination: {display}")

    def _choose_destination(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, "Choose export destination", ""
        )
        if folder:
            self._set_destination(folder)
            self.app.set_status(f"Export destination: {folder}")

    def _build_plan(self) -> ExportPlan | None:
        if not self._destination:
            self.app.set_status("Choose a destination folder first.")
            return None

        template_ids = self._checked_template_ids()
        if not template_ids:
            self.app.set_status("Select at least one template to export.")
            return None

        from pathlib import Path

        files: list[tuple[str, str]] = []
        for tid in template_ids:
            entry = template_by_id(tid)
            if not entry:
                continue
            content = self.app.store.get_content(tid)
            # Determine relative path
            if entry.normal_folder:
                rel = f"{entry.normal_folder}/{entry.filename}"
            else:
                rel = entry.filename
            files.append((rel, content))

        use_hidden = self.hidden_toggle.isChecked()
        plan = build_export_plan(Path(self._destination), files, use_hidden)
        return plan

    def _format_diff(self, lines: list[str]) -> str:
        """Helper to format diff lines for QTextEdit."""
        formatted = []
        for line in lines:
            if line.startswith('+'):
                formatted.append(f"<span style='color: #85e89d;'>{line}</span>")
            elif line.startswith('-'):
                formatted.append(f"<span style='color: #f85149;'>{line}</span>")
            elif line.startswith('@@'):
                formatted.append(f"<span style='color: #79c0ff;'>{line}</span>")
            else:
                formatted.append(line)
        return "<br>".join(formatted)

    def _on_preview(self) -> None:
        plan = self._build_plan()
        if plan is None:
            return

        self._current_plan = plan

        # Build HTML preview for diff support
        html = []
        mode = "hidden" if plan.use_hidden else "normal"
        html.append(f"<b>Destination:</b> {plan.destination}<br>")
        html.append(f"<b>Mode:</b> {mode}<br>")
        html.append(f"<b>Files:</b> {len(plan.items)}<br>")
        if plan.has_conflicts:
            html.append(f"<b>Conflicts:</b> <span style='color: #f85149;'>{len(plan.conflict_paths)}</span><br>")
        html.append("<br>")

        for item in plan.items:
            marker = " <span style='color: #f85149;'>⚠ EXISTS</span>" if item.conflict else ""
            html.append(f"&nbsp;&nbsp;<b>{item.relative_path}</b>{marker}<br>")

            if item.conflict:
                diff = item.diff_lines()
                if diff:
                    html.append("&nbsp;&nbsp;&nbsp;&nbsp;--- Diff ---<br>")
                    html.append(f"<div style='margin-left: 20px; font-family: monospace;'>{self._format_diff(diff[:20])}</div>")
                    if len(diff) > 20:
                        html.append(f"&nbsp;&nbsp;&nbsp;&nbsp;... ({len(diff) - 20} more lines)<br>")
                    html.append("&nbsp;&nbsp;&nbsp;&nbsp;------------<br><br>")

        self.preview_area.setHtml("".join(html))
        self.app.set_status(f"Preview: {len(plan.items)} files planned.")

    def _on_export(self) -> None:
        plan = self._build_plan()
        if plan is None:
            return

        self._current_plan = plan

        if plan.has_conflicts:
            conflicts = "\n".join(plan.conflict_paths)
            reply = QMessageBox.warning(
                self,
                "Existing Files",
                f"The following files already exist:\n\n{conflicts}\n\n"
                f"Overwrite them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            overwrite = reply == QMessageBox.StandardButton.Yes
        else:
            overwrite = False

        written = execute_export(plan, overwrite=overwrite)
        count = len(written)
        self.app.set_status(f"Exported {count} file{'s' if count != 1 else ''}.")

        # Update preview
        lines = [f"✓ Exported {count} files to:"]
        lines.append(str(plan.destination))
        lines.append("")
        for p in written:
            lines.append(f"  {p.relative_to(plan.destination)}")
        self.preview_area.setPlainText("\n".join(lines))
