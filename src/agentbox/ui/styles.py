# src/agentbox/ui/styles.py

STELLAR_STYLE = """
QWidget {
    background-color: #0A0C0D;
    color: #E2E8F0;
    font-family: ".AppleSystemUIFont", "SF Pro Text", "Inter", "Segoe UI", sans-serif;
    font-size: 13px;
    letter-spacing: 0px;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */

QFrame#sidebar {
    background-color: #0A0C0D;
    border-right: 1px solid #1C2024;
}

QScrollArea#sidebar_scroll {
    background: transparent;
    border: none;
}

QScrollArea#sidebar_scroll > QWidget {
    background: transparent;
}

QPushButton#sidebar_btn {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    color: #8B949E;
    font-size: 13px;
    font-weight: 500;
    padding: 8px 12px;
    text-align: left;
}

QPushButton#sidebar_btn:hover {
    background-color: #15181C;
    color: #C9D1D9;
}

QPushButton#sidebar_btn:checked {
    background-color: #1A1D21;
    color: #D9FF00;
}

QFrame#sidebar_sep {
    background-color: #1C2024;
    margin: 8px 12px;
}

/* ── Panels ──────────────────────────────────────────────────────────────── */

QFrame#surface_panel,
QFrame#template_list_panel,
QFrame#template_editor_panel {
    background-color: #111417;
    border: 1px solid #1C2024;
    border-radius: 10px;
}

QFrame#action_bar,
QFrame#converter_controls {
    background-color: #111417;
    border: 1px solid #1C2024;
    border-radius: 10px;
}

QSplitter#category_splitter,
QSplitter#converter_splitter {
    background-color: transparent;
}

QSplitter::handle {
    background-color: transparent;
    margin: 0 2px;
}

QSplitter::handle:hover {
    background-color: #D9FF00;
}

/* ── Labels ──────────────────────────────────────────────────────────────── */

QLabel {
    background: transparent;
    color: #C9D1D9;
}

QLabel#section_title {
    color: #F0F6FC;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: -0.2px;
}

QLabel#panel_label {
    color: #8B949E;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

QLabel#helper_text {
    color: #8B949E;
    line-height: 1.5;
}

QLabel#eyebrow {
    color: #D9FF00;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

/* ── Inputs ──────────────────────────────────────────────────────────────── */

QLineEdit,
QComboBox {
    background-color: #0A0C0D;
    border: 1px solid #2D333B;
    border-radius: 6px;
    color: #E2E8F0;
    min-height: 32px;
    padding: 4px 10px;
    selection-background-color: #D9FF00;
    selection-color: #0A0C0D;
}

QLineEdit:focus,
QComboBox:focus {
    border: 1px solid #D9FF00;
    background-color: #111417;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #0A0C0D;
    border: 1px solid #2D333B;
    border-radius: 6px;
    color: #E2E8F0;
    selection-background-color: #1A1D21;
    selection-color: #D9FF00;
    padding: 4px;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */

QPushButton {
    background-color: #21262D;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #C9D1D9;
    font-weight: 500;
    min-height: 32px;
    padding: 5px 16px;
}

QPushButton:hover {
    background-color: #30363D;
    border-color: #8B949E;
    color: #F0F6FC;
}

QPushButton:pressed {
    background-color: #1A1D21;
}

QPushButton#primary_action {
    background-color: #D9FF00;
    border: 1px solid #D9FF00;
    color: #0A0C0D;
    font-weight: 600;
}

QPushButton#primary_action:hover {
    background-color: #E5FF33;
    border-color: #E5FF33;
}

QPushButton#primary_action:pressed {
    background-color: #CCF000;
}

QPushButton#muted_action {
    background-color: transparent;
    border: 1px solid transparent;
    color: #8B949E;
    font-weight: 500;
}

QPushButton#muted_action:hover {
    background-color: #15181C;
    color: #C9D1D9;
}

QPushButton#toggle_btn {
    background-color: #0A0C0D;
    border: 1px solid #2D333B;
    color: #8B949E;
    font-weight: 500;
}

QPushButton#toggle_btn:checked {
    background-color: #1A1D21;
    border: 1px solid #D9FF00;
    color: #D9FF00;
}

QPushButton#danger_action {
    color: #FF7B72;
    border-color: #FF7B72;
    background-color: transparent;
}

QPushButton#danger_action:hover {
    background-color: #FF7B72;
    color: #0A0C0D;
}

/* ── Lists ───────────────────────────────────────────────────────────────── */

QListWidget,
QTextEdit {
    background-color: #0A0C0D;
    border: 1px solid #1C2024;
    border-radius: 8px;
    color: #E2E8F0;
    padding: 6px;
}

QTextEdit#code_view {
    font-family: "JetBrains Mono", "Menlo", "SF Mono", monospace;
    font-size: 13px;
    line-height: 1.5;
    border: none;
    background-color: transparent;
}

QListWidget#template_list,
QListWidget#export_list {
    outline: none;
    border: none;
    background-color: transparent;
}

QTextBrowser#markdown_view {
    background-color: transparent;
    border: none;
    color: #E2E8F0;
    font-size: 13px;
    line-height: 1.5;
}

QListWidget::item {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    color: #8B949E;
    margin: 2px 0px;
    padding: 8px 10px;
}

QListWidget::item:hover {
    background-color: #15181C;
    color: #C9D1D9;
}

QListWidget::item:selected {
    background-color: #1A1D21;
    color: #D9FF00;
}

QTextEdit:focus,
QTextBrowser:focus,
QListWidget:focus {
    border: 1px solid #D9FF00;
}

/* ── Scrollbars ──────────────────────────────────────────────────────────── */

QScrollBar:vertical {
    background-color: transparent;
    margin: 4px 2px 4px 0;
    width: 6px;
}

QScrollBar::handle:vertical {
    background-color: #2D333B;
    border-radius: 3px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #8B949E;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
    border: none;
    height: 0;
}

/* ── Status Bar ──────────────────────────────────────────────────────────── */

QStatusBar#status_bar {
    background-color: #0A0C0D;
    border-top: 1px solid #1C2024;
    color: #8B949E;
    padding: 4px 12px;
    font-size: 12px;
}
"""
