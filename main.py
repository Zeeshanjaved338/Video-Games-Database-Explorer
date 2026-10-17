"""
Video Game Database Explorer — Application Entry Point.
University CS200 Data Structures & Algorithms Project 1.
"""

import sys
import os

# Ensure current directory is on PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from database.repository import GameRepository
from services.data_service import DataService
from ui.main_window import MainWindow


def main():
    # Enable high DPI scaling on supported displays
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Video Game Database Explorer")
    app.setOrganizationName("CS200 Data Structures & Algorithms")

    # Initialize repository and data service
    repo = GameRepository()
    data_service = DataService(repo)

    # Launch Main Window
    window = MainWindow(data_service)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

