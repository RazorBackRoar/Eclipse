# src/eclipse/ui/category_panel.py
"""Category content panel — template list + editor for each category tab."""
from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..catalog import (
    TemplateEntry,
    UserTemplateStore,
    category_label,
    templates_for_category,
)


class TemplateList(QFrame):
    """Left sub-panel: lists templates in the selected category."""

    template_selected = Signal(str)  # emits template_id

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("template_list_panel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.title_label = QLabel("Templates")
        self.title_label.setObjectName("section_title")

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("template_list")
        self.list_widget.itemSelectionChanged.connect(self._on_selection)

        layout.addWidget(self.title_label)
        layout.addWidget(self.list_widget)

    def populate(self, category_id: str, store: UserTemplateStore) -> None:
        self.list_widget.clear()
        self.title_label.setText(category_label(category_id))
        entries = templates_for_category(category_id)

        if not entries:
            empty = QListWidgetItem("No templates in this category")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_widget.addItem(empty)
            return

        for entry in entries:
            edited_marker = " •" if store.is_edited(entry.id) else ""
            item = QListWidgetItem(f"{entry.display_name}{edited_marker}")
            item.setData(Qt.ItemDataRole.UserRole, entry.id)
            item.setToolTip(entry.filename)
            self.list_widget.addItem(item)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _on_selection(self) -> None:
        current = self.list_widget.currentItem()
        if current is None:
            return
        template_id = current.data(Qt.ItemDataRole.UserRole)
        if template_id:
            self.template_selected.emit(template_id)


class TemplateEditor(QFrame):
    """Right sub-panel: editable text area for the selected template."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("template_editor_panel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(8)

        self.filename_label = QLabel("Select a template")
        self.filename_label.setObjectName("section_title")

        self.preview_btn = QPushButton("Preview")
        self.preview_btn.setObjectName("toggle_btn")
        self.preview_btn.setCheckable(True)
        self.preview_btn.setFixedWidth(70)
        self.preview_btn.clicked.connect(self._on_preview_toggle)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setObjectName("muted_action")
        self.reset_btn.setToolTip("Reset to default content")
        self.reset_btn.setFixedWidth(70)

        header.addWidget(self.filename_label)
        header.addStretch(1)
        header.addWidget(self.preview_btn)
        header.addWidget(self.reset_btn)

        self.stack = QStackedWidget()

        self.editor = QTextEdit()
        self.editor.setObjectName("code_view")
        self.editor.setPlaceholderText("Select a template to view and edit its content.")

        self.preview = QTextBrowser()
        self.preview.setObjectName("markdown_view")
        self.preview.setOpenExternalLinks(True)

        self.stack.addWidget(self.editor)
        self.stack.addWidget(self.preview)

        layout.addLayout(header)
        layout.addWidget(self.stack)

    def set_template(self, entry: TemplateEntry, content: str) -> None:
        self.filename_label.setText(entry.display_name)
        self.editor.setPlainText(content)
        self._update_preview()

    def get_content(self) -> str:
        return self.editor.toPlainText()

    def clear(self) -> None:
        self.filename_label.setText("Select a template")
        self.editor.clear()
        self.preview.clear()

    def _update_preview(self) -> None:
        self.preview.setMarkdown(self.editor.toPlainText())

    def _on_preview_toggle(self) -> None:
        if self.preview_btn.isChecked():
            self._update_preview()
            self.stack.setCurrentIndex(1)
            self.preview_btn.setText("Edit")
        else:
            self.stack.setCurrentIndex(0)
            self.preview_btn.setText("Preview")


class CategoryPanel(QWidget):
    """Main content area for a category tab.

    Combines a template list (left) with an editor (right) and action bar (bottom).
    """

    export_requested = Signal(str, str, bool)  # template_id, content, use_hidden

    def __init__(self, app_controller: Any) -> None:
        super().__init__()
        self.app = app_controller
        self.current_category: str = ""
        self.current_template_id: str = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Splitter: template list | editor
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setObjectName("category_splitter")
        self.splitter.setChildrenCollapsible(False)

        self.template_list = TemplateList()
        self.template_list.template_selected.connect(self._on_template_selected)

        self.editor = TemplateEditor()
        self.editor.reset_btn.clicked.connect(self._on_reset)

        self.splitter.addWidget(self.template_list)
        self.splitter.addWidget(self.editor)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)

        layout.addWidget(self.splitter, 1)

        # Bottom action bar
        action_bar = QFrame()
        action_bar.setObjectName("action_bar")
        bar_layout = QHBoxLayout(action_bar)
        bar_layout.setContentsMargins(14, 10, 14, 10)
        bar_layout.setSpacing(12)

        self.save_btn = QPushButton("Save edits")
        self.save_btn.setObjectName("muted_action")
        self.save_btn.clicked.connect(self._on_save)

        bar_layout.addWidget(self.save_btn)
        bar_layout.addStretch(1)

        self.hidden_toggle = QPushButton("Hidden")
        self.hidden_toggle.setObjectName("toggle_btn")
        self.hidden_toggle.setCheckable(True)
        self.hidden_toggle.setToolTip("Export folders with a leading dot (.codex, .cursor, etc.)")

        self.export_btn = QPushButton("Export selected")
        self.export_btn.setObjectName("primary_action")
        self.export_btn.clicked.connect(self._on_export)

        bar_layout.addWidget(self.hidden_toggle)
        bar_layout.addWidget(self.export_btn)

        layout.addWidget(action_bar)

        # Setup shortcut
        shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut.activated.connect(self._on_save)

    def load_category(self, category_id: str) -> None:
        # Save current edits before switching
        self._auto_save()
        self.current_category = category_id
        self.current_template_id = ""
        self.template_list.populate(category_id, self.app.store)
        self.editor.clear()

    def _on_template_selected(self, template_id: str) -> None:
        # Save previous template edits
        self._auto_save()
        self.current_template_id = template_id
        from ..catalog import template_by_id
        entry = template_by_id(template_id)
        if entry:
            content = self.app.store.get_content(template_id)
            self.editor.set_template(entry, content)

    def _on_save(self) -> None:
        self._auto_save()
        self.app.set_status("Saved.")
        # Refresh list to update edited markers
        self.template_list.populate(self.current_category, self.app.store)

    def _on_reset(self) -> None:
        if self.current_template_id:
            self.app.store.reset_to_default(self.current_template_id)
            from ..catalog import template_by_id
            entry = template_by_id(self.current_template_id)
            if entry:
                self.editor.set_template(entry, entry.default_content)
            self.app.set_status("Reset to default.")
            self.template_list.populate(self.current_category, self.app.store)

    def _on_export(self) -> None:
        if self.current_template_id:
            self._auto_save()
            content = self.app.store.get_content(self.current_template_id)
            use_hidden = self.hidden_toggle.isChecked()
            self.app.export_template(self.current_template_id, content, use_hidden)

    def _auto_save(self) -> None:
        """Persist the current editor content if a template is loaded."""
        if self.current_template_id:
            content = self.editor.get_content()
            if content:
                self.app.store.set_content(self.current_template_id, content)
