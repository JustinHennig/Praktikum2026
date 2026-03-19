from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QHeaderView, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout
from app.storage.sqlite_database import insert_measurement_into_db
from app.storage.csv_writer import save_as_csv

class MeasurementDisplay(QGroupBox):
    def __init__(self):
        super().__init__("Measurement Display")

        layout = QVBoxLayout(self)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "Frequency", "Amplitude", "Peak-to-Peak", "RMS"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

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
        self.save_db_btn.clicked.connect(self.insert_measurement_into_db)
        self.clear_btn.clicked.connect(self.clear_display)

        self.measurement_data = []

    # function to save the measurement data as a CSV file
    def save_as_csv(self):
        save_as_csv(self.measurement_data)

    def clear_display(self):
        self.table.setRowCount(0)
        self.measurement_data.clear()
    
    def add_measurement(self, data):
        self.measurement_data.append(data)
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(data["Time"])))
        self.table.setItem(row, 1, QTableWidgetItem(str(data["Frequency"])))
        self.table.setItem(row, 2, QTableWidgetItem(str(data["Amplitude"])))
        self.table.setItem(row, 3, QTableWidgetItem(str(data["Peak-to-Peak"])))
        self.table.setItem(row, 4, QTableWidgetItem(str(data["RMS"])))

    def insert_measurement_into_db(self):
        for data in self.measurement_data:
            insert_measurement_into_db(
                time=data.get("Time"),
                freq=float(data.get("Frequency", 0)),
                amplitude=float(data.get("Amplitude", 0)),
                peak_to_peak=float(data.get("Peak-to-Peak", 0)),
                rms=float(data.get("RMS", 0)),
                v_div_mv=float(data.get("v_div_mv", 0)),
                t_div_ms=float(data.get("t_div_ms", 0)),
                offset_mv=float(data.get("offset_mv", 0)),
                trigger_level=float(data.get("trigger_level", 0))
            )