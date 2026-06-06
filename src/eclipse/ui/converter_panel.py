# src/agentbox/ui/converter_panel.py
"""Converter tab UI — paste or load text, choose formats, preview conversion."""
from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..converter import (
    FORMATS,
    available_targets,
    can_convert,
    convert,
    detect_format,
    format_label,
)


class ConverterPanel(QWidget):
    """Converter tab: select source/target formats, paste or load text, preview."""

    def __init__(self, app_controller: Any) -> None:
        super().__init__()
        self.app = app_controller

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        title = QLabel("Converter")
        title.setObjectName("section_title")

        helper = QLabel(
            "Convert between workspace config formats. "
            "Paste text or load a file, choose formats, and preview the result."
        )
        helper.setObjectName("helper_text")
        helper.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(helper)

        # Controls row
        controls = QFrame()
        controls.setObjectName("converter_controls")
        ctrl_layout = QHBoxLayout(controls)
        ctrl_layout.setContentsMargins(12, 10, 12, 10)
        ctrl_layout.setSpacing(12)

        ctrl_layout.addWidget(QLabel("From:"))
        self.source_combo = QComboBox()
        for f in FORMATS:
            self.source_combo.addItem(f["label"], f["id"])
        self.source_combo.currentIndexChanged.connect(self._on_source_changed)
        ctrl_layout.addWidget(self.source_combo)

        ctrl_layout.addWidget(QLabel("→"))

        ctrl_layout.addWidget(QLabel("To:"))
        self.target_combo = QComboBox()
        ctrl_layout.addWidget(self.target_combo)

        self.detect_btn = QPushButton("Auto-detect")
        self.detect_btn.setObjectName("muted_action")
        self.detect_btn.clicked.connect(self._on_detect)
        ctrl_layout.addWidget(self.detect_btn)

        self.load_btn = QPushButton("Load file…")
        self.load_btn.setObjectName("muted_action")
        self.load_btn.clicked.connect(self._on_load_file)
        ctrl_layout.addWidget(self.load_btn)

        ctrl_layout.addStretch(1)

        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setObjectName("primary_action")
        self.convert_btn.clicked.connect(self._on_convert)
        ctrl_layout.addWidget(self.convert_btn)

        layout.addWidget(controls)

        # Text areas
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("converter_splitter")
        splitter.setChildrenCollapsible(False)

        # Source
        source_frame = QFrame()
        source_frame.setObjectName("surface_panel")
        source_layout = QVBoxLayout(source_frame)
        source_layout.setContentsMargins(12, 12, 12, 12)
        source_layout.setSpacing(6)
        source_label = QLabel("Source")
        source_label.setObjectName("panel_label")
        self.source_editor = QTextEdit()
        self.source_editor.setObjectName("code_view")
        self.source_editor.setPlaceholderText("Paste source content here or load a file…")
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_editor)
        splitter.addWidget(source_frame)

        # Result
        result_frame = QFrame()
        result_frame.setObjectName("surface_panel")
        result_layout = QVBoxLayout(result_frame)
        result_layout.setContentsMargins(12, 12, 12, 12)
        result_layout.setSpacing(6)
        result_label = QLabel("Result")
        result_label.setObjectName("panel_label")
        self.result_editor = QTextEdit()
        self.result_editor.setObjectName("code_view")
        self.result_editor.setReadOnly(True)
        self.result_editor.setPlaceholderText("Converted output will appear here.")
        result_layout.addWidget(result_label)
        result_layout.addWidget(self.result_editor)
        splitter.addWidget(result_frame)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter, 1)

        # Bottom bar
        bottom = QHBoxLayout()
        bottom.setSpacing(12)

        self.export_result_btn = QPushButton("Export result…")
        self.export_result_btn.setObjectName("muted_action")
        self.export_result_btn.clicked.connect(self._on_export_result)

        bottom.addStretch(1)
        bottom.addWidget(self.export_result_btn)
        layout.addLayout(bottom)

        # Initialize target combo
        self._on_source_changed()

    def _on_source_changed(self) -> None:
        source = self.source_combo.currentData()
        self.target_combo.clear()
        if source:
            targets = available_targets(source)
            for t in targets:
                self.target_combo.addItem(format_label(t), t)

    def _on_detect(self) -> None:
        text = self.source_editor.toPlainText()
        if not text.strip():
            self.app.set_status("Paste text first to auto-detect format.")
            return
        detected = detect_format(text)
        if detected:
            idx = self.source_combo.findData(detected)
            if idx >= 0:
                self.source_combo.setCurrentIndex(idx)
            self.app.set_status(f"Detected: {format_label(detected)}")
        else:
            self.app.set_status("Could not auto-detect format.")

    def _on_load_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load source file", "",
            "Markdown files (*.md);;All files (*)",
        )
        if path:
            from pathlib import Path
            try:
                content = Path(path).read_text(encoding="utf-8")
                self.source_editor.setPlainText(content)
                self.app.set_status(f"Loaded: {Path(path).name}")
            except OSError as e:
                self.app.set_status(f"Failed to load: {e}")

    def _on_convert(self) -> None:
        source_id = self.source_combo.currentData()
        target_id = self.target_combo.currentData()
        text = self.source_editor.toPlainText()

        if not text.strip():
            self.app.set_status("Paste or load source text first.")
            return

        if not source_id or not target_id:
            self.app.set_status("Select source and target formats.")
            return

        if not can_convert(source_id, target_id):
            self.app.set_status(f"Cannot convert {source_id} → {target_id}.")
            return

        try:
            result = convert(text, source_id, target_id)
            self.result_editor.setPlainText(result)
            self.app.set_status(
                f"Converted {format_label(source_id)} → {format_label(target_id)}"
            )
        except Exception as e:
            self.app.set_status(f"Conversion error: {e}")

    def _on_export_result(self) -> None:
        content = self.result_editor.toPlainText()
        if not content.strip():
            self.app.set_status("Nothing to export. Run a conversion first.")
            return

        target_id = self.target_combo.currentData()
        suggested_name = "AGENTS.md"
        for f in FORMATS:
            if f["id"] == target_id:
                suggested_name = f["filename"]
                break

        path, _ = QFileDialog.getSaveFileName(
            self, "Export converted file", suggested_name,
            "Markdown files (*.md);;All files (*)",
        )
        if path:
            from pathlib import Path
            try:
                out = Path(path)
                if not content.endswith("\n"):
                    content += "\n"
                out.write_text(content, encoding="utf-8")
                self.app.set_status(f"Exported to: {out.name}")
            except OSError as e:
                self.app.set_status(f"Export failed: {e}")
