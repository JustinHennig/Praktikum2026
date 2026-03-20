import sys
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from utils.create_data_for_displa import inject_mock_data


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # Inject mock data for testing
    inject_mock_data(window) 
    app.exec()

if __name__ == "__main__":
    main()