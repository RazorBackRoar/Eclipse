# src/eclipse/ui/sidebar.py
"""Sidebar navigation for Eclipse workspace config manager."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..catalog import CATEGORIES


class SidebarButton(QPushButton):
    """A single navigation button in the sidebar."""

    def __init__(self, category_id: str, label: str) -> None:
        super().__init__(label)
        self.category_id = category_id
        self.setObjectName("sidebar_btn")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(34)


class Sidebar(QFrame):
    """Vertical sidebar with category navigation buttons."""

    category_selected = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(160)
        self.buttons: dict[str, SidebarButton] = {}
        self.separators: list[QFrame] = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Search bar
        search_container = QWidget()
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(10, 10, 10, 5)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self._on_search)

        search_layout.addWidget(self.search_input)
        outer.addWidget(search_container)

        scroll = QScrollArea()
        scroll.setObjectName("sidebar_scroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 5, 10, 14)
        layout.setSpacing(2)

        # Group categories
        current_group = ""
        for cat in CATEGORIES:
            group = cat.get("group", "")
            if group != current_group and current_group:
                sep = QFrame()
                sep.setObjectName("sidebar_sep")
                sep.setFixedHeight(1)
                self.separators.append(sep)
                layout.addWidget(sep)
            current_group = group

            btn = SidebarButton(cat["id"], cat["label"])
            btn.clicked.connect(self._on_click)
            self.buttons[cat["id"]] = btn
            layout.addWidget(btn)

        layout.addStretch(1)
        scroll.setWidget(container)

        outer.addWidget(scroll)

    def select(self, category_id: str) -> None:
        for cid, btn in self.buttons.items():
            btn.setChecked(cid == category_id)

    def _on_click(self) -> None:
        btn = self.sender()
        if isinstance(btn, SidebarButton):
            self.select(btn.category_id)
            self.category_selected.emit(btn.category_id)

    def _on_search(self, text: str) -> None:
        text = text.lower()
        for cid, btn in self.buttons.items():
            if text in btn.text().lower() or text in cid.lower():
                btn.show()
            else:
                btn.hide()

        # Hide separators if search is active
        for sep in self.separators:
            if text:
                sep.hide()
            else:
                sep.show()
