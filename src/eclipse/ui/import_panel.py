# src/eclipse/ui/import_panel.py
"""Import tab UI — scan workspace folders and import configs."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..catalog import category_label, template_by_id
from ..importer import ImportCandidate, scan_for_configs


class ImportPanel(QWidget):
    """Import tab: select a workspace folder, scan for configs, and import."""

    def __init__(self, app_controller: Any) -> None:
        super().__init__()
        self.app = app_controller
        self._candidates: list[ImportCandidate] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        title = QLabel("Import")
        title.setObjectName("section_title")

        helper = QLabel(
            "Scan a workspace folder for existing agent configurations "
            "and import them into your local template store."
        )
        helper.setObjectName("helper_text")
        helper.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(helper)

        # Main content: two columns
        content_layout = QHBoxLayout()
        content_layout.setSpacing(14)

        # Left: found files
        left_frame = QFrame()
        left_frame.setObjectName("surface_panel")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(8)

        list_header = QHBoxLayout()
        list_label = QLabel("Found Configurations")
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

        self.candidate_list = QListWidget()
        self.candidate_list.setObjectName("export_list")
        self.candidate_list.itemSelectionChanged.connect(self._on_selection_changed)

        left_layout.addLayout(list_header)
        left_layout.addWidget(self.candidate_list)

        content_layout.addWidget(left_frame, 1)

        # Right: preview
        right_frame = QFrame()
        right_frame.setObjectName("surface_panel")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(8)

        preview_label = QLabel("File Preview")
        preview_label.setObjectName("panel_label")
        self.preview_area = QTextEdit()
        self.preview_area.setObjectName("code_view")
        self.preview_area.setReadOnly(True)
        self.preview_area.setPlaceholderText(
            "Select a file from the list to preview its contents."
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

        self.source_label = QLabel("No workspace selected")
        self.source_label.setObjectName("helper_text")

        self.choose_source_btn = QPushButton("Scan folder…")
        self.choose_source_btn.setObjectName("muted_action")
        self.choose_source_btn.clicked.connect(self._choose_source)

        self.import_btn = QPushButton("Import selected")
        self.import_btn.setObjectName("primary_action")
        self.import_btn.clicked.connect(self._on_import)
        self.import_btn.setEnabled(False)

        bottom_layout.addWidget(self.source_label, 1)
        bottom_layout.addWidget(self.choose_source_btn)
        bottom_layout.addWidget(self.import_btn)

        layout.addWidget(bottom)

        # Initialize from active workspace if available
        self._load_active_workspace()

    def _load_active_workspace(self) -> None:
        from ..paths import get_workspace
        ws = get_workspace()
        if ws and ws.exists():
            self._scan_folder(ws)

    def _scan_folder(self, folder: Path) -> None:
        self.source_label.setText(f"Source: {folder}")
        self.app.set_status(f"Scanning {folder}...")

        self._candidates = scan_for_configs(folder)
        self.candidate_list.clear()
        self.preview_area.clear()

        if not self._candidates:
            self.app.set_status("No recognizable configurations found.")
            self.import_btn.setEnabled(False)
            return

        for idx, cand in enumerate(self._candidates):
            entry = template_by_id(cand.template_id)
            name = entry.display_name if entry else cand.relative_path
            cat_label = category_label(cand.category)

            item = QListWidgetItem(f"{cand.relative_path} → [{cat_label}] {name}")
            item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsSelectable
            )
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(Qt.ItemDataRole.UserRole, idx)
            self.candidate_list.addItem(item)

        self.import_btn.setEnabled(True)
        self.app.set_status(f"Found {len(self._candidates)} configurations.")

    def _choose_source(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, "Choose workspace to scan", ""
        )
        if folder:
            self._scan_folder(Path(folder))

    def _select_all(self) -> None:
        for i in range(self.candidate_list.count()):
            item = self.candidate_list.item(i)
            if item and item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                item.setCheckState(Qt.CheckState.Checked)

    def _select_none(self) -> None:
        for i in range(self.candidate_list.count()):
            item = self.candidate_list.item(i)
            if item and item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                item.setCheckState(Qt.CheckState.Unchecked)

    def _on_selection_changed(self) -> None:
        current = self.candidate_list.currentItem()
        if current is None:
            return
        idx = current.data(Qt.ItemDataRole.UserRole)
        if idx is not None and 0 <= idx < len(self._candidates):
            cand = self._candidates[idx]
            self.preview_area.setPlainText(cand.content)

    def _on_import(self) -> None:
        imported_count = 0
        for i in range(self.candidate_list.count()):
            item = self.candidate_list.item(i)
            if (
                item
                and item.flags() & Qt.ItemFlag.ItemIsUserCheckable
                and item.checkState() == Qt.CheckState.Checked
            ):
                idx = item.data(Qt.ItemDataRole.UserRole)
                if idx is not None and 0 <= idx < len(self._candidates):
                    cand = self._candidates[idx]
                    self.app.store.set_content(cand.template_id, cand.content)
                    imported_count += 1

        self.app.set_status(f"Successfully imported {imported_count} configurations.")
        self.app.store.save()
