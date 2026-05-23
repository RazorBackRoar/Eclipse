# src/agentbox/main.py
import sys

from PySide6.QtWidgets import QApplication

from agentbox.app import EclipseApp


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Eclipse")
    app.setApplicationDisplayName("Eclipse AI Workspace")

    window = EclipseApp()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
