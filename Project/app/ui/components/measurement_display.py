from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout

from app.storage.csv_writer import save_as_csv
from app.storage.sqlite_repository import save_to_database

class MeasurementDisplay(QGroupBox):
    def __init__(self):
        super().__init__("Measurement Display")

        layout = QVBoxLayout(self)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # z.B. Amplitude, Frequenz, RMS, Zeit
        self.table.setHorizontalHeaderLabels(["Amplitude", "Frequenz", "RMS", "Zeit"])

        # Daten hinzufügen:
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(amplitude)))
        self.table.setItem(row, 1, QTableWidgetItem(str(frequenz)))
        self.table.setItem(row, 2, QTableWidgetItem(str(rms)))
        self.table.setItem(row, 3, QTableWidgetItem(str(zeit)))

        # Buttons for saving
        button_row = QHBoxLayout()

        self.save_csv_btn = QPushButton("Save as CSV")
        self.save_db_btn = QPushButton("Save to Database")
        self.clear_btn = QPushButton("Clear Display")

        button_row.addWidget(self.save_csv_btn)
        button_row.addWidget(self.save_db_btn)
        button_row.addWidget(self.clear_btn)
        layout.addLayout(button_row)

        # Signals
        self.save_csv_btn.clicked.connect(self.save_as_csv)
        self.save_db_btn.clicked.connect(self.save_to_database)
        self.clear_btn.clicked.connect(self.clear_display)

    def save_as_csv(self):
        save_as_csv()

    def save_to_database(self):
        save_to_database()

    def clear_display(self):
        # Placeholder for clearing the measurement display
        print("Clear Display clicked")