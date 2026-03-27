# This is the main file of the application, which creates the main window and starts the application.

import sys
import os
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from utils.mock_data_measurement_display import inject_mock_data


def _load_qss(filename: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "app", "ui", "styling", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(_load_qss("theme_dark.qss"))
    window = MainWindow()
    window.show()
    #Inject mock data for testing, this can be removed when the actual measurement data is being used
    #inject_mock_data(window) 
    app.exec()

if __name__ == "__main__":
    main()