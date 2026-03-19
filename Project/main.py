import sys
from PySide6.QtWidgets import QApplication
from app.storage.sqlite_database import get_connection, init_db
from app.ui.main_window import MainWindow


def main():
    print(get_connection())
    init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()