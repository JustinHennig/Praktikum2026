# This file defines the MeasurementDisplay class, which is using a QGroupbox to display
# the measurement data in a table and also provides buttons to save the data, load the data, clear the display and delete a selected row.

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QHeaderView, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QDialog
from PySide6.QtCore import Signal
from app.storage.sqlite_database import insert_measurement_settings, insert_measurement, get_measurements_by_id, get_all_measurement_settings
from app.ui.components.load_delete_measurement_window import LoadMeasurementDialog

class MeasurementDisplay(QGroupBox):
     # Signal to notify the main window that a new measurement has been added, so that the configuration can be updated
    configuration_loaded = Signal(dict)

    def __init__(self):
        super().__init__("Measurement Display")

        layout = QVBoxLayout(self)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "Col. 1", "Col. 2", "Col. 3", "Col. 4"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Buttons for saving
        button_row = QHBoxLayout()

        self.save_db_btn = QPushButton("Save to Database")
        self.load_db_btn = QPushButton("Load from Database")
        self.clear_btn = QPushButton("Clear Display")
        self.delete_row_btn = QPushButton("Delete Row")

        button_row.addWidget(self.save_db_btn)
        button_row.addWidget(self.load_db_btn)
        button_row.addWidget(self.clear_btn)
        button_row.addWidget(self.delete_row_btn)
        layout.addLayout(button_row)

        # Signals
        self.save_db_btn.clicked.connect(self.insert_measurement_into_db)
        self.load_db_btn.clicked.connect(self.load_measurements_from_db)
        self.clear_btn.clicked.connect(self.clear_display)
        self.delete_row_btn.clicked.connect(self.delete_selected_row)

        # Initialize measurement data list
        self.measurement_data = []

    # Function to add measurement data to the display
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

    # Function to load the measurement data from the database and display it in the table
    def load_measurements_from_db(self):
        settings = get_all_measurement_settings()
        if not settings:
            QMessageBox.information(self, "Load", "No measurements found in the database.")
            return

        dialog = LoadMeasurementDialog(settings, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        # Check if a measurement was selected
        if dialog.selected_id is None:
            QMessageBox.information(self, "Load", "No measurement selected.")
            return
        
        # Load the measurement entries for the selected measurement_id
        measurements = get_measurements_by_id(dialog.selected_id)
        if not measurements:
            QMessageBox.information(self, "Load", "No data rows for this measurement.")
            return
        
        # Look for the corresponding settings to reconstruct the configuration in the panel
        selected_settings = next((s for s in settings if s["measurement_id"] == dialog.selected_id), None)
        if selected_settings is not None:
            self.configuration_loaded.emit(selected_settings)  # Emit the configuration to update the device panel

        self.clear_display()
        for m in measurements:
            # Reconstruct a flat dict matching what add_measurement expects
            data = {"Time": m["time"], **m["values"]}
            self.add_measurement(data)

    # Function to clear the display
    def clear_display(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "Col. 1", "Col. 2", "Col. 3", "Col. 4"])
        self.measurement_data.clear()

    # Function to delete the selected row
    def delete_selected_row(self):
        selected_row = self.table.currentRow()
        self.table.removeRow(selected_row)
        # Only delete if index exists in measurement_data
        if 0 <= selected_row < len(self.measurement_data):
            del self.measurement_data[selected_row]