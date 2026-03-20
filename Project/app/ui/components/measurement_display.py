from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QHeaderView, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout
from app.storage.sqlite_database import insert_measurement_settings, insert_measurement
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
        self.table.setEditTriggers(QTableWidget.AllEditTriggers)
        layout.addWidget(self.table)

        # Buttons for saving
        button_row = QHBoxLayout()

        self.save_csv_btn = QPushButton("Save as CSV")
        self.save_db_btn = QPushButton("Save to Database")
        self.clear_btn = QPushButton("Clear Display")
        self.add_row_btn = QPushButton("Add Row")

        button_row.addWidget(self.save_csv_btn)
        button_row.addWidget(self.save_db_btn)
        button_row.addWidget(self.clear_btn)
        button_row.addWidget(self.add_row_btn)
        layout.addLayout(button_row)

        # Signals
        self.save_csv_btn.clicked.connect(self.save_as_csv)
        self.save_db_btn.clicked.connect(self.insert_measurement_into_db)
        self.clear_btn.clicked.connect(self.clear_display)
        self.add_row_btn.clicked.connect(self.add_empty_row)
        
    def add_empty_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        # Optional: Leere Zellen erzeugen
        for col in range(self.table.columnCount()):
            self.table.setItem(row, col, QTableWidgetItem(""))

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
        if not self.measurement_data:
            return
        # Settings aus erstem Messpunkt extrahieren
        settings = self.measurement_data[0]
        measurement_id = insert_measurement_settings(
            v_div_mv=float(settings.get("v_div_mv", 0)),
            t_div_ms=float(settings.get("t_div_ms", 0)),
            offset_mv=float(settings.get("offset_mv", 0)),
            trigger_level=float(settings.get("trigger_level", 0))
        )
        # Alle Messpunkte speichern
        for data in self.measurement_data:
            insert_measurement(
                measurement_id=measurement_id,
                time=data.get("Time"),
                freq=float(data.get("Frequency", 0)) if data.get("Frequency") is not None else None,
                amplitude=float(data.get("Amplitude", 0)) if data.get("Amplitude") is not None else None,
                peak_to_peak=float(data.get("Peak-to-Peak", 0)) if data.get("Peak-to-Peak") is not None else None,
                rms=float(data.get("RMS", 0)) if data.get("RMS") is not None else None
            )