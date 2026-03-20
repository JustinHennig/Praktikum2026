from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QHeaderView, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout
from app.storage.sqlite_database import insert_measurement_settings, insert_measurement
from app.storage.csv_writer import save_as_csv

class MeasurementDisplay(QGroupBox):
    def __init__(self):
        super().__init__("Measurement Display")

        layout = QVBoxLayout(self)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "Col. 1", "Col. 2", "Col. 3", "Col. 4"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.AllEditTriggers)
        layout.addWidget(self.table)

        # Buttons for saving
        button_row = QHBoxLayout()

        self.save_csv_btn = QPushButton("Save as CSV")
        self.save_db_btn = QPushButton("Save to Database")
        self.clear_btn = QPushButton("Clear Display")
        self.add_row_btn = QPushButton("Add Row")
        self.delete_row_btn = QPushButton("Delete Row")

        button_row.addWidget(self.save_csv_btn)
        button_row.addWidget(self.save_db_btn)
        button_row.addWidget(self.clear_btn)
        button_row.addWidget(self.add_row_btn)
        button_row.addWidget(self.delete_row_btn)
        layout.addLayout(button_row)

        # Signals
        self.save_csv_btn.clicked.connect(self.save_as_csv)
        self.save_db_btn.clicked.connect(self.insert_measurement_into_db)
        self.clear_btn.clicked.connect(self.clear_display)
        self.add_row_btn.clicked.connect(self.add_empty_row)
        self.delete_row_btn.clicked.connect(self.delete_selected_row)

        # Initialize measurement data list
        self.measurement_data = []

    # Function to add a row to the table (for mock data)
    def add_empty_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col in range(self.table.columnCount()):
            self.table.setItem(row, col, QTableWidgetItem(""))
        # Add empty data to measurement_data to avoid errors
        self.measurement_data.append({})

    # Function to delete the selected row
    def delete_selected_row(self):
        selected_row = self.table.currentRow()
        self.table.removeRow(selected_row)
        # Only delete if index exists in measurement_data
        if 0 <= selected_row < len(self.measurement_data):
            del self.measurement_data[selected_row]

        self.measurement_data = []

    # function to save the measurement data as a CSV file
    def save_as_csv(self):
        save_as_csv(self.measurement_data)

    def clear_display(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.measurement_data.clear()
    
    def add_measurement(self, data):
        self.measurement_data.append(data)

        # Keys to display — skip metadata that is not useful in the table
        skip_keys = {"Resource", "Channel"}
        columns = [k for k in data if k not in skip_keys]

        # On the first row, update the table headers to match the actual data keys
        if self.table.rowCount() == 0:
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)

        row = self.table.rowCount()
        self.table.insertRow(row)
        for col, key in enumerate(columns):
            value = data.get(key)
            self.table.setItem(row, col, QTableWidgetItem("" if value is None else str(value)))

    def insert_measurement_into_db(self):
        if not self.measurement_data:
            return

        # Keys that are never stored as measurement values
        meta_keys = {"Resource", "Time"}
        # Keys that describe the instrument configuration → go into 'parameters'
        config_keys = {"Channel", "v_div_mv", "t_div_ms", "offset_mv", "trigger_level"}

        first = self.measurement_data[0]

        # Device is identified by the instrument resource address
        device = first.get("Resource", "Unknown")

        # Configuration: channel + oscilloscope settings (ignored for generator since those keys won't exist)
        parameters = {k: v for k, v in first.items() if k in config_keys}

        # Measurement value keys: everything that is not metadata or configuration
        measurement_keys = [k for k in first if k not in meta_keys and k not in config_keys]

        try:
            measurement_id = insert_measurement_settings(
                device=device,
                parameters=parameters,
            )
            for data in self.measurement_data:
                values = {k: data.get(k) for k in measurement_keys}
                insert_measurement(
                    measurement_id=measurement_id,
                    time=data.get("Time", ""),
                    values=values
                )
            QMessageBox.information(
                self,
                "Saved",
                f"{len(self.measurement_data)} measurement(s) saved to the database."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save to database:\n{e}")