# src/eclipse/ui/main_window.py
"""Main window widget — sidebar + content area layout."""
from __future__ import annotations

from typing import Any

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from .category_panel import CategoryPanel
from .converter_panel import ConverterPanel
from .export_panel import ExportPanel
from .import_panel import ImportPanel
from .sidebar import Sidebar
from .styles import STELLAR_STYLE


class MainWindowWidget(QWidget):
    """Central widget: sidebar navigation + stacked content panels."""

    def __init__(self, app_controller: Any) -> None:
        super().__init__()
        self.app = app_controller
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet(STELLAR_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.category_selected.connect(self._on_category)
        body.addWidget(self.sidebar)

        # Stacked content
        self.stack = QStackedWidget()

        # Category panel (shared for all template categories)
        self.category_panel = CategoryPanel(self.app)
        self.stack.addWidget(self.category_panel)  # index 0

        # Converter panel
        self.converter_panel = ConverterPanel(self.app)
        self.stack.addWidget(self.converter_panel)  # index 1

        # Export panel
        self.export_panel = ExportPanel(self.app)
        self.stack.addWidget(self.export_panel)  # index 2

        # Import panel
        self.import_panel = ImportPanel(self.app)
        self.stack.addWidget(self.import_panel) # index 3

        body.addWidget(self.stack, 1)
        root.addLayout(body, 1)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("status_bar")
        root.addWidget(self.status_bar)

        # Global Shortcuts
        self.export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        self.export_shortcut.activated.connect(self._cmd_export)

        self.workspace_shortcut = QShortcut(QKeySequence("Ctrl+,"), self)
        self.workspace_shortcut.activated.connect(self._cmd_workspace)

        # Select first category
        self.sidebar.select("general")
        self.category_panel.load_category("general")

    def _on_category(self, category_id: str) -> None:
        if category_id == "converter":
            self.stack.setCurrentIndex(1)
        elif category_id == "export":
            self.stack.setCurrentIndex(2)
        elif category_id == "import":
            self.stack.setCurrentIndex(3)
        else:
            self.stack.setCurrentIndex(0)
            self.category_panel.load_category(category_id)

    def _cmd_export(self) -> None:
        self.sidebar.select("export")
        self._on_category("export")

    def _cmd_workspace(self) -> None:
        self.app.switch_workspace()

    def set_status(self, msg: str) -> None:
        self.status_bar.showMessage(msg, 7000)
